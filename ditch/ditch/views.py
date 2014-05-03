# Create your views here.
from __future__ import absolute_import

from django.views.generic import TemplateView,FormView

class HomeView(TemplateView):
    template_name = 'home.html'

class AboutView(TemplateView):
    template_name = 'about.html'



