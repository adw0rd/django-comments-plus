# coding: utf-8
import re

from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.conf import settings
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from comments_plus.models import CommentPlus

COMMENTS_PLUS_CONFIRM_EMAIL = getattr(settings, 'COMMENTS_PLUS_CONFIRM_EMAIL', True)


def comment_exists(comment):
    return (CommentPlus.objects.filter(
            user_name=comment.user_name,
            user_email=comment.user_email,
            submit_date=comment.submit_date).count() > 0)


def notify_comment_followers(comment):
    followers = {}
    previous_comments = CommentPlus.objects.filter(
        object_pk=comment.object_pk, is_public=True,
        followup=True).exclude(id__exact=comment.id)

    for instance in previous_comments:
        followers[instance.user_email] = instance.user_name

    # Data
    model = models.get_model(comment.content_type.app_label, comment.content_type.model)
    target = model._default_manager.get(pk=comment.object_pk)
    site = Site.objects.get_current()

    # URL's
    unsubscribe_url = reverse("comments-plus-unsubscribe",
        kwargs={'content_type_id': ContentType.objects.get_for_model(target._meta.concrete_model).pk, 'object_id': target.pk})
    subscriptions_manage_url = reverse("comments-plus-subscriptions-manage")

    # Build username
    if comment.user_name:
        comment_user_name = comment.user_name
    elif comment.user:
        if all((comment.user.first_name, comment.user.last_name)):
            comment_user_name = "{} {}".format(comment.user.first_name, comment.user.last_name)
        else:
            comment_user_name = comment.user.username

    context = Context({
        'comment_user_name': comment_user_name,
        'comment_comment': email_text_quote(comment.comment, width=10, prefix="|"),
        'comment': comment,
        'target': target,
        'protocol': 'http',
        'site_name': site.name,
        'site_domain': site.domain,
        'unsubscribe_url': unsubscribe_url,
        'subscriptions_manage_url': subscriptions_manage_url,
        })

    # Prepare text message
    text_message_template = loader.get_template("comments_plus/email_followup_comment.txt")
    text_message = text_message_template.render(context)

    # Prepare html message
    html_message_template = loader.get_template("comments_plus/email_followup_comment.html")
    html_message = html_message_template.render(context)

    # Subject
    subject_template = loader.get_template("comments_plus/email_followup_comment_subject.txt")
    subject = subject_template.render(context)

    for email, name in followers.iteritems():
        if not email:
            continue
        #send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        message = EmailMultiAlternatives(subject, text_message, settings.DEFAULT_FROM_EMAIL, [email])
        message.attach_alternative(html_message, "text/html")
        message.send()


def send_email_confirmation_request(user_data, comment, target,
                                    text_template="comments_plus/email_confirmation_request.txt",
                                    html_template="comments_plus/email_confirmation_request.html",
                                    use_https=False):
    subject = _("User and comment confirmation request")
    confirmation_url = reverse("comments-plus-confirm", kwargs={'uidb36': user_data.get('uidb36'), 'token': user_data.get('token')})
    site = Site.objects.get_current()

    # Prepare context
    context = {
        'user_data': user_data,
        'comment': comment,
        'target': target,
        'protocol': use_https and 'https' or 'http',
        'site_name': site.name,
        'site_domain': site.domain,
        'contact': settings.DEFAULT_FROM_EMAIL,
        'target_name': _(target._meta.object_name),
        'target_link': target.get_absolute_url(),
        'confirmation_url': confirmation_url,
    }
    context = Context(context)

    # Prepare text message
    text_message_template = loader.get_template(text_template)
    text_message = text_message_template.render(context)

    # Prepare html message
    html_message_template = loader.get_template(html_template)
    html_message = html_message_template.render(context)

    # Create message
    message = EmailMultiAlternatives(subject, text_message, settings.DEFAULT_FROM_EMAIL, [user_data.get('email')])
    message.attach_alternative(html_message, "text/html")
    message.send()


def on_comment_was_posted(sender, comment, target, user_data, request, **kwargs):
    """
    Post the comment if a user is authenticated
        or register a user and send a confirmation email.

    On signal django.contrib.comments.signals.comment_was_posted check if the
    user is authenticated or if settings.COMMENTS_PLUS_CONFIRM_EMAIL is False.
    In both cases will post the comment. Otherwise will send a confirmation
    email to the person who posted the comment.
    """
    if comment.user:
        if request.user.is_authenticated() and request.user.is_active:
            comment.is_public = True
            comment.save()
            notify_comment_followers(comment)
        else:
            # Send confirmation email
            send_email_confirmation_request(user_data=user_data, comment=comment, target=target)


def email_text_quote(text, width=10, prefix="|"):
    items = []
    words = re.findall(r'[^\s]+', text, re.UNICODE)
    while words:
        chunk = words[0:width]
        del words[0:width]
        items.append(u"{} {}".format(prefix, u" ".join(chunk)))
    return u"\n".join(items)
