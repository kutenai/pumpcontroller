
import csv
from django.conf import settings

from django.contrib import admin as a
from django.contrib.comments import Comment
from django.contrib.auth.models import User,Group
from django.contrib.auth.admin import UserAdmin
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.contrib.admin.util import label_for_field

from account.models import AccountDeletion, Account, SignupCode, EmailAddress
from account.admin import SignupCodeAdmin


class DitchAdminSite(a.AdminSite):
    @never_cache
    def index(self, request, extra_context=None):
        context = {'title': 'Schematics.com Administration'}
        for model, model_admin in self._registry.items():
            setattr(model._meta, 'verbose_name_plural', unicode(model._meta.verbose_name_plural))
        response = super(DitchAdminSite, self).index(request, extra_context=context)
        return response

site = DitchAdminSite()
