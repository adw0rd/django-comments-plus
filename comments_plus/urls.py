from django.conf.urls import patterns, include, url
from comments_plus.views import PostView, ConfirmView, UnsubscribeView, SubscriptionsManageView


urlpatterns = patterns('',
    url(r'^post/$', PostView.as_view(), name='comments-plus-post'),
    url(r'^confirm/(?P<uidb36>.+)/(?P<token>.+)/$', ConfirmView.as_view(), name='comments-plus-confirm'),
    url(r'^unsubscribe/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', UnsubscribeView.as_view(), name="comments-plus-unsubscribe"),
    url(r'^subscriptions/$', SubscriptionsManageView.as_view(), name="comments-plus-subscriptions-manage"),
    url(r'', include("django.contrib.comments.urls")),
)
