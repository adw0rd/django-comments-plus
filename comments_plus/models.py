# coding: utf8
from django.db import models
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class CommentPlusManager(models.Manager):
    def for_app_models(self, *args):
        content_types = []
        for app_model in args:
            app, model = app_model.split(".")
            content_types.append(ContentType.objects.get(app_label=app, model=model))
        return self.for_content_types(content_types)

    def for_content_types(self, content_types):
        qs = self.get_query_set().filter(content_type__in=content_types).reverse()
        return qs


class CommentPlus(Comment):
    followup = models.BooleanField(help_text=_("Receive by email further comments in this conversation"), blank=True)
    is_review = models.BooleanField(default=False)
    REVIEW_TYPE_CHOICES = (
        ('positive', u'Положительная'),
        ('neutral', u'Нейтральная'),
        ('negative', u'Отрицательная'),
    )

    REVIEW_TYPE_COLORS = {
        'positive': '#ebf8ec',
        'negative': '#ffefef',
    }

    review_type = models.CharField(choices=REVIEW_TYPE_CHOICES, max_length=8, null=True, blank=True)
    review_title = models.CharField(max_length=100, null=True, blank=True)

    def review_type_color(self):
        return self.REVIEW_TYPE_COLORS.get(self.review_type, '')

    objects = CommentPlusManager()

    def __unicode__(self):
        return self.comment

    class Meta:
        verbose_name = u"Comment"
        verbose_name_plural = u"Comments"
