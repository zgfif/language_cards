from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from core.forms import SignInForm, SignUpForm


class IndexView(View):
    def get(self, request):
        context = dict()
        context['message'] = request.session.get('message', 'No message')
        context['greeting'] = request.session.get('greeting', 'No')

        return render(request=request, context=context, template_name='index.html')


class SignUpView(TemplateView):
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SignUpForm
        return context

    def post(self, request):
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            request.session['message'] = 'Congratulations! You have successfully registered!'
            return redirect('/')
        return self.render_to_response(context={'form': form})


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
