from django import forms 
from api.models import *

from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']