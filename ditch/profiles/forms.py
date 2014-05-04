
from __future__ import absolute_import

import django.forms as f
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils import six

from account import forms as acc_f

safe_trans = lazy(mark_safe, six.text_type)

class SignUpForm(acc_f.SignupForm):

    email = f.EmailField(label="", widget=f.TextInput(attrs={'placeholder': _('Email Address'),}))
    preferred_name = f.CharField(label="", widget=f.TextInput(attrs={'placeholder': _('Screen Name'),}))
    password = f.CharField(label="", widget=f.PasswordInput(attrs={'placeholder': _('Password'),}))
    password_confirm = f.CharField(label="", widget=f.PasswordInput(attrs={'placeholder': _('Confirm Password'),}))

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ["email", "preferred_name", "password", "password_confirm",]

class LoginForm(acc_f.LoginEmailForm):

    email = f.CharField(label="", widget=f.TextInput(attrs={'placeholder': _('Username'), "class": ""}))
    password = f.CharField(label="", widget=f.PasswordInput(attrs={'placeholder': _('Password'), "class": ""}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ["email", "password",]

class PasswordResetForm(acc_f.PasswordResetForm):

    email = f.CharField(label="", widget=f.TextInput(attrs={'placeholder': _('Email Address'),}))

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

class UserAccountForm(f.ModelForm):

    email = f.CharField(label="Email")
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name",)

