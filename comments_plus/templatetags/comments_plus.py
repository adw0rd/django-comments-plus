# coding: utf-8
# from django.contrib.contenttypes.models import ContentType
from django import template

register = template.Library()


@register.tag
def get_comments_plus_list(parser, token):
    """
    Gets the list of comments for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comments_list for [object] as [varname]  %}
        {% get_comments_list for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_comments_list for blog_post as comments_list %}
        {% for comment in comments_list %}
            ...
        {% endfor %}

    """
    return None  # CommentListNode.handle_token(parser, token)


# @register.simple_tag
# def get_last_comments(*models):
#     results = []
#     # def sep(value):
#     #     items = []
#     #     if model.find('.'):
#     #         app_label, model = model.split('.')
#     #         content_type = ContentType.objects.get(app_label=app_label, model=model)
#     #         items.append(content_type)
#     #     return items
#     # content_types = map(sep, models)
#        model = models.get_model(*content_type.split("."))
#     return results
