# coding: utf-8
from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from models import CommentPlus

COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)
COMMENTS_PLUS_IGNORE_FIELDS = getattr(settings, 'COMMENTS_PLUS_IGNORE_FIELDS', [])


class CommentPlusForm(CommentForm):
    followup = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Notify me of follow up comments via email"))

    # REVIEW_TYPE_CHOICES = (
    #     ('positive', u'Положительная'),
    #     ('neutral', u'Нейтральная'),
    #     ('negative', u'Отрицательная'),
    # )
    # review_type = forms.ChoiceField(choices=REVIEW_TYPE_CHOICES, required=False)
    # review_title = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.get('user')
            del kwargs['user']
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(
            label=_("Username"),
            help_text=_("Required for user create"))
        self.fields['email'] = forms.EmailField(
            label=_("Email address"),
            help_text=_("Required for comment verification"))
        self.fields['comment'] = forms.CharField(
            widget=forms.Textarea(attrs={'placeholder': _('Your comment')}),
            max_length=COMMENT_MAX_LENGTH)
        for field_name in self.fields.keys():
            if field_name in COMMENTS_PLUS_IGNORE_FIELDS:
                self.fields[field_name].required = False

    def clean(self, *a, **kw):
        cleaned_data = self.cleaned_data
        if not self.data.get("email") and self.user.is_authenticated():
            # Если не указан email вообще и пользователь авторизован
            if not self.user.email:
                # Но у него не введен email (например из-за того что авторизация была через соц. сети)
                self._errors["email"] = self.error_class([
                    _(u'You must <a href="%(profile_link)s">provide your email address in your profile</a>') %
                    {'profile_link': reverse('user_profile')}])
        return cleaned_data

    def get_comment_model(self):
        return CommentPlus

    def get_comment_create_data(self):
        data = super(CommentForm, self).get_comment_create_data()
        data['followup'] = self.cleaned_data.get('followup')
        if settings.COMMENTS_PLUS_CONFIRM_EMAIL:
            data['is_public'] = False
        return data
