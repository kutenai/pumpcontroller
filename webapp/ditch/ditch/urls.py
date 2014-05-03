from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'ditch.views.home'),
    url(r'^mon/', include ('ditchmon.urls')),
    url(r'^ctrl/', include ('ditchctrl.urls')),

)
