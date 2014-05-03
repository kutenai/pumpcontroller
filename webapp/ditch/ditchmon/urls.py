from django.conf.urls import patterns, include, url

from views import index,levels

urlpatterns = patterns('',
    # Examples:
    url(r'^$', index),
    url(r'^levels$', levels),
)
