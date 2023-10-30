from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from core.forms import SignInForm, SignUpForm, AddWordForm
from core.models import Word
from core.lib.word_ids import WordIds


class IndexView(View):
    def get(self, request):
        context = {'words': []}
        if request.user.is_authenticated:
            words = Word.objects.filter(added_by=request.user)

            context['words'] = words

            # update learning ids
            WordIds(request, words).update()

        return render(request=request, template_name='index.html', context=context)


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
            messages.success(request, 'Congratulations! You have successfully registered!')
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


class AccountView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request=request, template_name='profile.html')
        return redirect('/signin')


class AddWordView(TemplateView):
    template_name = 'add_word.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/signin')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddWordForm()
        return context

    def post(self, request):
        form = AddWordForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/')

        return self.render_to_response(context={'form': form})


class WordListView(View):
    def get(self, request):
        if request.user.is_authenticated:
            words = Word.objects.filter(added_by=request.user)
            context = {'words': words}

            WordIds(request, words).update()

            return render(request, template_name='words.html', context=context)

        return redirect('/signin')


class LearningPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            words = Word.objects.filter(added_by=request.user.id)
            ru_word = words.first().id if words else None
            en_word = words.first().id if words else None
            context = {'learn_ru_word': ru_word, 'learn_en_word': en_word}
            return render(request, template_name='training_.html', context=context)
        return redirect('/signin')


class FromEng(View):
    direction = 'ru'

    def get(self, request, id):
        if request.user.is_authenticated:
            ids = request.session.get('word_ids', [])

            if ids and (len(ids) == 1 or ids[-1] == id):
                next_id = ids[0]
            elif ids:
                current_position = ids.index(id)
                next_id = ids[current_position + 1]
            else:
                next_id = None

            word = Word.objects.filter(id=id, added_by=request.user.id)[0]
            context = {'word': word, 'word_ids': ids, 'next_id': next_id, 'direction': self.direction}
            return render(request, template_name='training.html', context=context)
        return redirect('/signin')


class FromRu(FromEng):
    direction = 'en'


class DeleteWordView(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            word = get_object_or_404(Word, id=id)
            if word and word.added_by == request.user:
                word.delete()
                messages.success(request, 'Congratulations! You have successfully deleted word')
            else:
                messages.error(request, 'error! something went wrong...')

            return redirect('/words')
        else:
            return redirect('/signin')


class EditWordView(TemplateView):
    # template_name = 'add_word.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/signin')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Word, id=kwargs['id'])

        context = {'form': AddWordForm(initial={'word': item.word, 'translation': item.translation, 'sentence': item.sentence})}

        return render(request, template_name='add_word.html', context=context)

    def post(self, request, id):
        item = get_object_or_404(Word, id=id)

        form = AddWordForm(request.POST)

        if form.is_valid():
            form.update(request, item)
            return redirect('/words')
        return self.render_to_response(context={'form': form})
