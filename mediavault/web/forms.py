from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput,
                               required=True)

    class Meta:
        model = User
