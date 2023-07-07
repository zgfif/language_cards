from django.contrib.auth import logout
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView

from core.forms import SignInForm


class IndexView(View):
    def get(self, request):
        return render(request=request, template_name='index.html')


class SignUpView(View):
    def get(self, request):
        return render(request=request, template_name='signup.html')


class SignInView(FormView):
    form_class = SignInForm
    template_name = 'signin.html'
    success_url = '/'

    def form_valid(self, form):
        form.auth(self.request)

        return super().form_valid(form)


class SignOutView(View):
    def get(self, request):
        logout(self.request)
        return render(request=request, template_name='index.html')
