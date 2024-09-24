import json
from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from core.forms import SignInForm, SignUpForm, AddWordForm, StudyingLanguageForm
from core.lib.next_list_item import NextListItem
from core.lib.translate_text import TranslateText
from core.models import Word, MyUser
from core.lib.word_ids import WordIds


class IndexView(View):
    def get(self, request):
        context = {}

        if request.user.is_authenticated:
            words = Word.objects.filter(added_by=request.user, studying_lang=request.user.profile.studying_lang)

            context['has_words'] = True if words else False

            # update learning ids
            WordIds(request, words).update()
            context['studying_to_native_ids'] = request.session.get('studying_to_native_ids', [])
            context['native_to_studying_ids'] = request.session.get('native_to_studying_ids', [])
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
            profile = MyUser.objects.get(id=request.user.id)

            context = {
                    'auth_token': Token.objects.get(user_id=profile.id).key,
                    'total': profile.words.count(),
                    'known': profile.known_words.count(),
                    'unknown': profile.unknown_words.count(),
                    'form': StudyingLanguageForm,
            }

            return render(request=request, template_name='profile.html', context=context)
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
            return redirect(reverse('words'))
        return self.render_to_response(context={'form': form})


class WordListView(View):
    def get(self, request):
        if request.user.is_authenticated:
            auth_token = Token.objects.get_or_create(user=request.user)[0].key

            words = Word.objects.filter(added_by=request.user, studying_lang=request.user.profile.studying_lang).order_by('know_studying_to_native',
                                                                        'know_native_to_studying')

            WordIds(request, words).update()

            context = {'words': words,
                       'studying_to_native_ids': request.session.get('studying_to_native_ids'),
                       'native_to_studying_ids': request.session.get('native_to_studying_ids'),
                       'auth_token': auth_token,
                       }

            return render(request, template_name='words.html', context=context)

        return redirect('/signin')


class LearningPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user_words = Word.objects.filter(added_by=request.user.id)
            unknown_studying_to_native = user_words.filter(know_studying_to_native=False)
            unknown_native_to_studying = user_words.filter(know_native_to_studying=False)

            native_word = unknown_studying_to_native.first().id if unknown_studying_to_native else None
            studying_word = unknown_native_to_studying.first().id if unknown_native_to_studying else None

            context = {'learn_ru_word': native_word, 'learn_en_word': studying_word}
            return render(request, template_name='training_.html', context=context)
        return redirect('/signin')


class FromEng(View):
    direction = 'ru'

    def ids(self):
        return self.request.session.get('studying_to_native_ids', [])

    def get(self, request, id):
        if request.user.is_authenticated:
            # calculate the next word id for reference
            ids = self.ids()


            next_id = NextListItem(ids, id).calculate()

            word = Word.objects.filter(id=id, added_by=request.user.id)[0]
            context = {'word': word, 'ids': ids, 'next_id': next_id, 'direction': self.direction}
            return render(request, template_name='training.html', context=context)
        return redirect('/signin')

    def post(self, request, id):
        try:
            obj = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(data={'error': 'JsonError'})

        word = get_object_or_404(Word, id=id)

        if word.added_by == request.user:
            if obj['direction'] == 'ru':
                word.know_studying_to_native = obj['correctness']
            else:
                word.know_native_to_studying = obj['correctness']

            word.save()
        return JsonResponse(data={'some': 'leti leti'})


class FromRu(FromEng):
    direction = 'en'

    def ids(self):
        return self.request.session.get('native_to_studying_ids', [])


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
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/signin')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Word, id=kwargs['id'])

        context = {'form': AddWordForm(initial={'word': item.word, 'translation': item.translation, 'sentence': item.sentence})}

        return render(request, template_name='edit_word.html', context=context)

    def post(self, request, id):
        item = get_object_or_404(Word, id=id)

        form = AddWordForm(request.POST)

        if form.is_valid():
            form.update(request, item)
            return redirect('/words')
        return self.render_to_response(context={'form': form})


class ResetWordView(View):
    def get(self, request, id):
        word = get_object_or_404(Word, id=id)

        if request.user.is_authenticated and word.added_by == request.user:
            word.know_native_to_studying, word.know_studying_to_native = False, False
            word.save()
        return redirect('/words')


class TranslateWord(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            translation = TranslateText('en', 'ru').perform(body.get('text', ''))
        except json.JSONDecodeError:
            return JsonResponse(data={'error': 'JsonError'})
        return JsonResponse(data={'translation': translation})


