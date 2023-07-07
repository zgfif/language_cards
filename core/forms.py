from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.widgets.PasswordInput())

    def clean(self):
        print('haajl;fkajsdf;lkajsdf')
        user = User.objects.filter(username=self.cleaned_data['username']).first()
        if not user or not user.check_password(self.cleaned_data['password']):
            raise forms.ValidationError('Incorrect username/password')

    def auth(self, request):
        user = authenticate(request, **self.cleaned_data)
        login(request, user)
        return user
