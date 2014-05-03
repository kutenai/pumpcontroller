from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
#admin.autodiscover()
from views import index,levels

urlpatterns = patterns('',
    url(r'^$', index),
    url(r'/level$', levels),
)
