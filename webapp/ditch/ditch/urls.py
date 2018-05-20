from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ditch.views.home', name='home'),
    # url(r'^ditch/', include('ditch.foo.urls')),
    url(r'^$', 'ditch.views.home'),
    url(r'^mon/', include ('ditchmon.urls')),
    url(r'^ctrl/', include ('ditchctrl.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
