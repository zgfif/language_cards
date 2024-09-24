from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User
from django.core import validators

from core.lib.generate_audio import GenerateAudio
from core.models import Word, StudyingLanguage, STUDYING_LANGUAGES


class SignInForm(forms.Form):
    username = forms.CharField(widget=forms.widgets.TextInput(attrs={'class': 'form-control',
                                                                     'placeholder': 'email or username'}),
                               label='username/email')
    password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class': 'form-control',
                                                                         'placeholder': 'your password'}))

    def clean(self):
        user = User.objects.filter(username=self.cleaned_data['username']).first()

        if not user:
            user = User.objects.filter(email=self.cleaned_data['username']).first()

        if not user or not user.check_password(self.cleaned_data['password']):
            raise forms.ValidationError('Incorrect username/email/password')

    def auth(self, request):
        user = authenticate(request, **self.cleaned_data)
        if user is not None:
            messages.success(request, f'Hello! {user}')
            login(request, user)
        return user


class SignUpForm(forms.Form):
    username = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'must be unique'}))

    password = forms.CharField(required=True,
                               widget=forms.widgets.PasswordInput(attrs={'class': 'form-control',
                                                                         'placeholder': 'make up any password'}),)
    password_confirmation = forms.CharField(required=True,
                                            widget=forms.widgets.PasswordInput(attrs={'class': 'form-control',
                                                                                      'placeholder':
                                                                                          'must the same as password'}))

    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'mail@example.com'}),
                             validators=[validators.EmailValidator(message="Invalid Email")])

    def clean(self):
        by_username = User.objects.filter(username=self.cleaned_data['username']).first()
        by_email = User.objects.filter(email=self.cleaned_data['email']).first()

        if self.cleaned_data['password'] != self.cleaned_data['password_confirmation']:
            raise forms.ValidationError('Password and Password confirmation must be the same')
        if by_username or by_email:
            raise forms.ValidationError('Entered username or/and email is already exists')

    def save(self):
        self.cleaned_data.pop('password_confirmation')
        get_user_model().objects.create_user(**self.cleaned_data)


class AddWordForm(forms.Form):
    word = forms.CharField(label='word',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'in english'}))

    translation = forms.CharField(label='translation',
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'in russian'}))

    sentence = forms.CharField(label='sentence',
                               required=False,
                               widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder':
                                   'example of sentence in english'}))

    def clean(self):
        word = self.cleaned_data.get('word')
        translation = self.cleaned_data.get('translation')
        if not word:
            raise forms.ValidationError('You have not entered any word!')
        if word and not translation:
            raise forms.ValidationError(f'You have not added translation for {word}!')

    def save(self, request):
        try:
            sl = request.user.profile.studying_lang
            word = Word.objects.create(added_by=request.user, studying_lang=sl, **self.cleaned_data)
            GenerateAudio(word).perform()

        except:
            messages.error(request, 'Something went wrong!')
        else:
            messages.success(request, f'{self.cleaned_data.get("word")} was successfully added to your learn list!')

    def update(self, request, word):
        try:
            word.word = request.POST['word']
            word.sentence = request.POST['sentence']
            word.translation = request.POST['translation']
            word.save()
        except:
            messages.error(request, 'Something went wrong!')
        else:
            messages.success(request, f'{self.cleaned_data.get("word")} was successfully updated!')


class StudyingLanguageForm(forms.Form):
    name = forms.ChoiceField(label="", widget=forms.Select(attrs={'class': 'form-select'}), choices=STUDYING_LANGUAGES) 

