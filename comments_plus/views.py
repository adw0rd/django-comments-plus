# coding: utf-8
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseForbidden
from django.db import models, IntegrityError
from django.views.generic import ListView, View
from django.shortcuts import redirect
from django.utils.text import Truncator
from django.utils.translation import ugettext as _
from django.utils.http import int_to_base36, base36_to_int
from django.contrib import comments
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

from comments_plus.models import CommentPlus
from comments_plus.utils import on_comment_was_posted, notify_comment_followers
from comments_plus.mixins import JsonResponseMixin


class PostView(JsonResponseMixin, View):
    def post(self, request):
        context = {'status': 'failed'}
        errors = {}

        data = request.POST.copy()
        if request.user.is_authenticated():
            if not data.get('name', ''):
                data["name"] = request.user.username
            if not data.get('email', ''):
                data["email"] = request.user.email
        if "name" in data:
            data["name"] = Truncator(data["name"]).chars(50)

        model = models.get_model(*data.get('content_type').split('.'))
        target_object = model._default_manager.get(pk=data.get('object_pk'))
        # Receive the target object
        if hasattr(target_object, 'get_target_for_comment'):
            # If object provide the get_target method, then we must use it
            target = target_object.get_target_for_comment()
        else:
            target = target_object

        comment_form = comments.get_form()(target, data=data, user=request.user)

        if comment_form.security_errors():
            errors['security'] = comment_form.security_errors()

        if comment_form.is_valid():
            comment_data = comment_form.clean()
            user_data = {}

            try:
                if request.user.is_authenticated():
                    user = request.user
                else:
                    # Create a user
                    user_password = User.objects.make_random_password()
                    user = User(username=comment_data.get('name'), email=comment_data.get('email'))
                    user.set_password(user_password)
                    user.save()

                    # Build a activation key
                    token = token_generator.make_token(user=user)

                    user_data = {
                        'username': user.username,
                        'email': user.email,
                        'password': user_password,
                        'uidb36': int_to_base36(user.id),
                        'token': token,
                    }
            except (IntegrityError, ), exc:
                for field in ('name', 'email'):
                    if "{}'".format(field) in exc.args[1]:
                        errors[field] = exc.args[1]
            else:
                # Create the comment
                comment = comment_form.get_comment_object()
                comment.ip_address = request.META.get("REMOTE_ADDR", None)
                comment.user = user
                comment.is_public = False
                # If the user is authorized, the comment will be published immediately
                comments.signals.comment_will_be_posted.send(
                    sender=comment.__class__,
                    comment=comment,
                    request=request)
                comment.save()

                # Otherwise, comment will be a published after confirmation by email
                comments.signals.comment_was_posted.send(
                    sender=comment.__class__,
                    comment=comment,
                    target=target,
                    user_data=user_data,
                    request=request)

                # XXX: Я так и не выяснил причину того почему comment тут стает вдруг "is_public=True",
                # хотя до сигнала "comment_was_posted" он "is_public=False", поэтому ставлю временную заглушку:
                if hasattr(comment.user, 'profile') and comment.user.profile.is_confirmed:
                    comment.is_public = True
                else:
                    comment.is_public = False
                comment.save()

                # Next URL to relocation (see comments-plus.js)
                context['next'] = "{url}#comment-{pk}".format(url=data.get('next', '') or '', pk=comment._get_pk_val())

                if not request.user.is_authenticated():
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    auth_login(request, user)
        else:
            errors.update(comment_form.errors)

        if errors:
            context['errors'] = errors
        else:
            context['status'] = 'success'

        return self.render_to_response(context)


class ConfirmView(View):
    def dispatch(self, request, uidb36, token):
        # Checking the verify token and fetch the user
        assert uidb36 is not None and token is not None
        try:
            uid_int = base36_to_int(uidb36)
            user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            user = None
        if user is not None and token_generator.check_token(user, token):
            # validlink = True
            user.is_active = True
            user.save()
        else:
            # validlink = False
            raise User.DoesNotExist

        comments = CommentPlus.objects.filter(user=user).order_by('-submit_date')
        comments.update(is_public=True)
        comment = comments[0]
        model = models.get_model(comment.content_type.app_label, comment.content_type.model)
        target = model._default_manager.get(pk=comment.object_pk)

        # Notify followers
        notify_comment_followers(comment)

        if not request.user.is_authenticated():
            # Authentication
            user.backend = 'kinsburg_tv.users.backends.ActivationBackend'
            auth_login(request, user)

        messages.add_message(request, messages.INFO, _('Your comment has successfully and the account activated!'))
        return redirect(reverse('film', kwargs={"pk": target.pk, "slug": target.slug}))


class UnsubscribeView(JsonResponseMixin, View):
    def dispatch(self, request, content_type_id, object_id):
        try:
            ctype = ContentType.objects.get(pk=content_type_id)
            target = ctype.get_object_for_this_type(pk=object_id)
        except ctype.model_class().DoesNotExist:
            raise Http404

        comments = CommentPlus.objects.filter(content_type_id=content_type_id, object_pk=object_id, user=request.user)
        if not comments.exists():
            return HttpResponseForbidden("<h1>403 Forbidden</h1>")

        # Unsubscribe!
        comments.update(followup=False)

        if request.GET.get('json', False):
            # If request from javascript, then reponse as JSON
            return self.render_to_response({'status': 'success'})
        else:
            # Otherwise redirect to target url and draw message
            message = u"{}: {}".format(_('You have successfully unsubscribed from the comments to'), unicode(target))
            messages.add_message(request, messages.INFO, message)
            return redirect(target.get_absolute_url())


class SubscriptionsManageView(ListView):
    template_name = "comments_plus/subscriptions_manage.html"
    context_object_name = "subscriptions"

    def get_queryset(self, *a, **kw):
        user_id = getattr(self.request.user, 'pk', 0)
        queryset = CommentPlus.objects.select_related('content_type')\
            .filter(user=user_id, followup=True)\
            .distinct('content_type', 'object_pk')\
            .order_by('-submit_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SubscriptionsManageView, self).get_context_data(**kwargs)
        context['user_'] = self.request.user
        return context


comments.signals.comment_was_posted.connect(on_comment_was_posted)
