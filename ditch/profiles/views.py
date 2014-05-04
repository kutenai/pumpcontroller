from __future__ import absolute_import

import json

from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from social.apps.django_app.default.models import UserSocialAuth

from account import views as v
from account.forms import ChangePasswordForm

from .forms import (
    UserAccountForm,
    SignUpForm,PasswordResetForm,
    LoginForm
)

from ditchlib.view_utils import DitchMixin,get_redirect

class SignUpView(DitchMixin,v.SignupView):
    template_name = "signup.html"
    form_class = SignUpForm

    def generate_username(self, form):
        return form.cleaned_data.get('email')

    def get_context_data(self, *args, **kwargs):
        context = super(SignUpView, self).get_context_data(*args,   **kwargs)
        context.update({
            "social_action": "Sign in",
            "redirect_url": get_redirect(self.request),
            })
        return context

class LoggedInView(DitchMixin,TemplateView):
    template_name = 'logged-in.html'

    def get(self,r,*args,**kwargs):

        if not r.user.is_authenticated():
            print("Anonymous user.. what the heck!")
        else:
            print("Got a real user:%s" % r.user.last_name)
            print("Logged in.. ")

        return super(LoggedInView,self).get(r,*args,**kwargs)

class LoginView(DitchMixin,v.LoginView):
    template_name = "login.html"
    form_class = LoginForm

    def get_context_data(self, *args, **kwargs):
        context = super(LoginView, self).get_context_data(*args,   **kwargs)
        next = get_redirect(self.request)
        context.update({
            "social_action": "Sign in",
            "redirect_url": get_redirect(self.request),
            "next": ("?next=%s" % next if next else ""),
            })
        return context

class PasswordResetView(DitchMixin,v.PasswordResetView):
    template_name = "password_reset.html"
    form_class = PasswordResetForm

    def dispatch(self, *args, **kwargs):
        return super(PasswordResetView, self).dispatch(*args, **kwargs)

class UserAccountView(DitchMixin,TemplateView):
    template_name = 'user.html'

    def get(self,request,uid=None):
        """
        Get the user data
        """
        context = self.get_context_data()
        context['uid'] = uid

        print("User id:%s" % uid)

        return self.render_to_response(context)


class ChangePasswordView(DitchMixin,v.ChangePasswordView):

    def post(self, r, *args, **kwargs):
        resp = super(ChangePasswordView, self).post(r, *args, **kwargs)
        if not isinstance(resp, HttpResponseRedirect):
            return resp
        else:
            r.user.set_password(r.POST.get('password_new'))
            return redirect("account_settings")

    def dispatch(self, *args, **kwargs):
        return super(ChangePasswordView, self).dispatch(*args, **kwargs)

