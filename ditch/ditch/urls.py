from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
#admin.autodiscover()

from views import AboutView,HomeView

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(),name='home'),
    url(r'^mon/', include ('ditchmon.urls'),name='mon'),
    url(r'^ctrl/', include ('ditchctrl.urls'),name='ctrl'),
    url(r'^about/', AboutView.as_view(),name='ctrl'),
)
