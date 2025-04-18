import json
from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from core.forms import SignInForm, SignUpForm, AddWordForm, StudyingLanguageForm
from core.lib.next_list_item import NextListItem
from core.lib.translate_text import TranslateText
from core.models import Word, MyUser
from core.lib.word_ids import WordIds
# from core.tasks import reset_word_progress
from core.lib.update_word_progress import UpdateWordProgress
from core.lib.calculate_user_progress import CalculateUserProgress


class IndexView(View):
    def get(self, request):
        template_name = 'index.html'
        context = {}

        if request.user.is_authenticated:
            words = Word.objects.filter(added_by=request.user, 
                                        studying_lang=request.user.profile.studying_lang)

            context['has_words'] = True if words else False
            # update learning ids
            WordIds(request, words).update()

            context.update({
                'other_languages': request.user.profile.available_languages,
                'auth_token': request.user.auth_token,
                'studying_lang': request.user.profile.studying_lang,
                'studying_to_native_ids': request.session.get('studying_to_native_ids', []),
                'native_to_studying_ids': request.session.get('native_to_studying_ids', []),
            })

            calc = CalculateUserProgress(request.user, request.user.profile.studying_lang)
            
            context.update({
                'native_studying_progress': calc.perform('native_to_studying'),
                'studying_native_progress': calc.perform('studying_to_native'),
            })

        return render(request=request, template_name=template_name, context=context)


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
        messages.success(request, 'See ya!')
        return redirect('/')


class ProfileView(View):
    def get(self, request):
        if request.user.is_authenticated:
            profile = MyUser.objects.get(id=request.user.id)

            context = {
                    'auth_token': request.user.auth_token,
                    'total': profile.words.count(),
                    'known': profile.known_words.count(),
                    'unknown': profile.unknown_words.count(),
                    'form': StudyingLanguageForm,
                    'other_languages': request.user.profile.available_languages,
                    'studying_lang': request.user.profile.studying_lang,
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

        # this is used to switch studying language in two clicks 
        context.update({
            'auth_token': self.request.user.auth_token,
            'studying_lang': self.request.user.profile.studying_lang,
            'other_languages': self.request.user.profile.available_languages,
            'form': AddWordForm(),
        })

        sl = self.request.user.profile.studying_lang
        
        if sl:
            context.update({
                'sl_short': sl,
                'sl_full': sl.full_name.lower(),
            })

        return context

    def post(self, request):
        form = AddWordForm(request.POST)
        
        if form.is_valid():
            form.save(request)
            return redirect(reverse('add_word'))
        return self.render_to_response(context={'form': form})


class WordListView(View):
    def get(self, request):
        if request.user.is_authenticated:
            studying_lang = request.user.profile.studying_lang

            words = Word.objects.filter(added_by=request.user, studying_lang=studying_lang).order_by('know_studying_to_native', 'know_native_to_studying')

            WordIds(request, words).update()

            context = {
                'words': words,
                'studying_to_native_ids': request.session.get('studying_to_native_ids'),
                'native_to_studying_ids': request.session.get('native_to_studying_ids'),
                'auth_token': request.user.auth_token,
                'other_languages': request.user.profile.available_languages,
                'studying_lang': request.user.profile.studying_lang,
            }
            
            if studying_lang: 
                context['sl_short'] = studying_lang.name

            return render(request, template_name='words.html', context=context)

        return redirect('/signin')


class ExercisesPageView(View):
    def get(self, request):
        template_name = 'exercises_page.html'

        if request.user.is_authenticated:
            # other_languages and auth_token are used to switch studying language in nav bar
            context = {
                'other_languages': request.user.profile.available_languages, 
                'auth_token': request.user.auth_token,
                'studying_lang': request.user.profile.studying_lang,
                'sl_full_name': request.user.profile.studying_lang.full_name if request.user.profile.studying_lang else None,
            }
            
            user_words = Word.objects.filter(added_by=request.user.id, 
                                             studying_lang=request.user.profile.studying_lang)
            
            unknown_studying_to_native = user_words.filter(know_studying_to_native=False)
            unknown_native_to_studying = user_words.filter(know_native_to_studying=False)

            native_word = unknown_studying_to_native.first().id if unknown_studying_to_native else None
            studying_word = unknown_native_to_studying.first().id if unknown_native_to_studying else None


            context.update({'learn_ru_word': native_word, 
                            'learn_en_word': studying_word, 
                            'count_unknown_native_to_studying': unknown_native_to_studying.count(),
                            'count_unknown_studying_to_native': unknown_studying_to_native.count(),
                })
            
            studying_lang = request.user.profile.studying_lang

            if studying_lang:
                context['sl_short'] = studying_lang.name

            return render(request, template_name=template_name, context=context)
        return redirect('/signin')


class StudyingToNativeCard(View):
    DIRECTION = 'studying_to_native'

    def ids(self):
        return self.request.session.get('studying_to_native_ids', [])

    def get(self, request, id):
        if request.user.is_authenticated:
            # calculate the next word id for reference
            ids = self.ids()

            next_id = NextListItem(ids, id).calculate()

            word = Word.objects.filter(id=id, added_by=request.user.id)[0]
            
            context = {
                'word': word, 
                'studying_language': word.studying_lang, 
                'ids': ids, 
                'next_id': next_id, 
                'direction': self.DIRECTION,
                'studying_lang': word.studying_lang, # this variable has influence on notification 'please, choose studying..'
            }

            return render(request, template_name='translation_exercise.html', context=context)
        return redirect('/signin')

    def post(self, request, id):
        try:
            obj = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(data={'error': 'JsonError'})

        word = get_object_or_404(Word, id=id)

        if word.added_by == request.user:
            correctness = obj['correctness']
            if correctness:
                UpdateWordProgress(word).perform()

            if obj['direction'] == 'studying_to_native':
                word.know_studying_to_native = correctness
            else:
                word.know_native_to_studying = correctness

            word.save()
        return JsonResponse(data={'status': 'ok'})


class NativeToStudyingCard(StudyingToNativeCard):
    DIRECTION = 'native_to_studying'

    def ids(self):
        return self.request.session.get('native_to_studying_ids', [])


class DeleteWordView(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            word = get_object_or_404(Word, id=id)
            if word and word.added_by == request.user:
                word.delete()
                messages.success(request, f'Congratulations! You have successfully deleted \"{word.word}\"')
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

        initial_values = {
            'word': item.word, 
            'translation': item.translation, 
            'sentence': item.sentence
        }
        
        context = {
            'form': AddWordForm(initial=initial_values), 
            'sl_short': item.studying_lang, 
            'sl_full': item.studying_lang.full_name,
            'auth_token': request.user.auth_token,
            'studying_lang': request.user.profile.studying_lang,
        }

        return render(request, template_name='edit_word.html', context=context)

    def post(self, request, id):
        item = get_object_or_404(Word, id=id)

        form = AddWordForm(request.POST)
        if form.is_valid():
            form.update(request, item)
            return redirect('/words')
        return render(request, template_name='edit_word.html', context={'form': form})


class ResetWordView(View):
    def get(self, request, id):
        word = get_object_or_404(Word, id=id)

        if request.user.is_authenticated and word.added_by == request.user:
            word.reset_progress()
        return redirect('/words')


class TranslateApi(View):
    def post(self, request):
        body = json.loads(request.body)
        source_lang, text = body.get('source_lang', ''), body.get('text', '') 
        
        translation = TranslateText(source_lang=source_lang, target_lang='ru').perform(text=text)

        if not translation: 
            translation = '' 

        return JsonResponse({
            'status': 'ok',
            'translation': translation,
        })

