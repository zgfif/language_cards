import json

from django.core.exceptions import ValidationError
from django.utils.timezone import localtime
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.lib.remove_file import RemoveFile
from core.lib.remove_from_gcs import RemoveFromGcs
from core.models import Word, MyUser, GttsAudio, StudyingLanguage, Profile
from core.lib.translate_text import TranslateText
from core.lib.next_list_item import NextListItem
from core.lib.generate_audio import GenerateAudio


class IndexViewTests(TestCase):
    def test_has_sign_in_reference(self):
        response = self.client.get('/')
        text = 'Sign in'
        self.assertContains(response, text=text, status_code=200)

    def test_has_add_word_reference(self):
        User.objects.create_user(username='pasha', password='1asdfX', email='pasha@gmail.com')
        self.client.login(username='pasha', password='1asdfX')
        response = self.client.get('/')
        self.assertContains(response, 'add_word')


class SignUpViewTests(TestCase):
    def test_have_form_to_signup(self):
        response = self.client.get('/signup')
        text = 'Password confirmation'
        self.assertContains(response, text=text, status_code=200)

    def test_successful_registration(self):
        user_data = {
            'username': 'pasha',
            'email': 'zihzag@gmail.com',
            'password': '12345678',
            'password_confirmation': '12345678',
        }

        response = self.client.post('/signup', user_data, follow=True)
        text = 'Congratulations! You have successfully registered!'
        u = User.objects.last()
        t = Token.objects.last()
        self.assertEqual(u.email, user_data['email'])
        self.assertEqual(t.user_id, u.id)
        self.assertContains(response, text=text, status_code=200)

    def test_if_username_is_busy(self):
        user_data = {
            'username': 'pasha',
            'email': 'zihzag@gmail.com',
            'password': '12345678',
        }

        User.objects.create_user(**user_data)

        post_data = {
            'username': 'pasha',
            'email': 'pasha@gmail.com',
            'password': '1234',
            'password_confirmation': '1234'
        }

        response = self.client.post('/signup', post_data)
        text = 'Entered username or/and email is already exists'
        self.assertContains(response, text=text, status_code=200)

    def test_if_email_is_busy(self):
        user_data = {
            'username': 'pasha',
            'email': 'zihzag@gmail.com',
            'password': '12345678',
        }

        User.objects.create_user(**user_data)

        post_data = {'username': 'Pavel', 'email': 'zihzag@gmail.com', 'password': '1234',
                     'password_confirmation': '1234'}

        response = self.client.post('/signup', post_data)
        text = 'Entered username or/and email is already exists'
        self.assertContains(response, text=text, status_code=200)

    def test_if_password_and_password_confirmation_different(self):
        post_data = {'username': 'Pavel', 'email': 'zihzag@gmail.com', 'password': '1234',
                     'password_confirmation': '12345'}
        response = self.client.post('/signup', post_data)
        text = 'Password and Password confirmation must be the same'
        self.assertContains(response, text=text, status_code=200)


class SignInViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='pasha', password='1asdfX', email='zihzag@gmail.com')

    def test_has_form_to_signin(self):
        response = self.client.get('/signin')
        self.assertContains(response, text='password', status_code=200)
        self.assertContains(response, text='username/email', status_code=200)

    def test_incorrect_username(self):
        response = self.client.post('/signin', {'username': 'dima', 'password': '1asdfX'})
        self.assertContains(response, text='Incorrect username/email/password', status_code=200)
        self.assertNotContains(response, text='Sign out', status_code=200)

    def test_incorrect_email(self):
        response = self.client.post('/signin', {'username': 'pasha@gmail.com', 'password': '1asdfX'})
        self.assertContains(response, text='Incorrect username/email/password', status_code=200)
        self.assertNotContains(response, text='Sign out', status_code=200)

    def test_incorrect_password(self):
        response = self.client.post('/signin', {'username': 'zihzag@gmail.com', 'password': '111111'})
        self.assertContains(response, text='Incorrect username/email/password', status_code=200)
        self.assertNotContains(response, text='Sign out', status_code=200)

    def test_by_email(self):
        response = self.client.post('/signin', {'username': 'zihzag@gmail.com', 'password': '1asdfX'}, follow=True)
        self.assertContains(response, text='Hello', status_code=200)
        self.assertContains(response, text='Sign out', status_code=200)

    def test_by_username(self):
        response = self.client.post('/signin', {'username': 'pasha', 'password': '1asdfX'}, follow=True)
        self.assertContains(response, text='Hello', status_code=200)
        self.assertContains(response, text='Sign out', status_code=200)


class LogOutViewTests(TestCase):
    def test_logout(self):
        User.objects.create_user(username='pasha', password='1asdfX')

        self.client.login(username='pasha', password='1asdfX')
        response_before_logout = self.client.get('/')

        self.assertContains(response_before_logout, text='Sign out', status_code=200)

        response = self.client.get('/signout')
        self.assertContains(response, text='Sign in', status_code=200)


class AccountViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='pasha', password='1asdfX', email='pasha@gmail.com')

    def test_opening_profile_without_authorization(self):
        response = self.client.get('/profile', follow=True)
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_access_to_account_with_authorization(self):
        self.client.login(username='pasha', password='1asdfX')

        response = self.client.get('/profile')

        self.assertContains(response, text='pasha', status_code=200)
        self.assertContains(response, text='pasha@gmail.com', status_code=200)
        self.assertContains(response, text=localtime().date())


class AddWordViewTests(TestCase):
    # this function removes all unnecessary gTTS files which are saved in the media/ directory during tests
    def tearDown(self):
        files_to_remove = GttsAudio.objects.all().values_list('audio_name', flat=True)

        for filename in files_to_remove:
            if filename:
                RemoveFile(filename).perform()
                # RemoveFromGcs().perform(filename)

    def test_access_to_form_for_not_authorized_user(self):
        response = self.client.get('/add_word', follow=True)
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_access_to_form_for_authorized_user(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}
        User.objects.create_user(**credentials)
        self.client.login(**credentials)

        response = self.client.get('/add_word')

        self.assertContains(response, text='word', status_code=200)
        self.assertContains(response, text='translation')
        self.assertContains(response, text='sentence')
        self.assertContains(response, text='add')

    def test_adding_word_to_dictionary(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}

        sl = StudyingLanguage.objects.create(name='en')

        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        u = User.objects.create_user(**credentials)
        u.profile.studying_lang = sl
        u.profile.save()
        self.client.login(**credentials)
        
        response = self.client.post('/add_word', word_details, follow=True)
        success_message = f'{word_details["word"]} was successfully added to your learn list!'
        self.assertEqual(Word.objects.filter(word=word_details['word']).count(), 1)
        self.assertContains(response, text=success_message, status_code=200)

    def test_adding_word_to_dictionary_without_translation(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}

        word_details = {
            'word': 'smallpox',
            'translation': '',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        User.objects.create_user(**credentials)
        self.client.login(**credentials)

        response = self.client.post('/add_word', word_details)
        failure_message = f'You have not added translation for {word_details["word"]}!'
        self.assertContains(response, text=failure_message, status_code=200)

    def test_adding_word_to_dictionary_without_sentence(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}

        sl = StudyingLanguage.objects.create(name='en')

        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': '',
            'studying_lang_id': sl.id
        }
        u = User.objects.create_user(**credentials)
        u.profile.studying_lang = sl
        u.profile.save()

        self.client.login(**credentials)

        response = self.client.post('/add_word', word_details, follow=True)
        success_message = f'{word_details["word"]} was successfully added to your learn list!'
        self.assertEqual(Word.objects.filter(word=word_details['word']).count(), 1)
        self.assertContains(response, text=success_message, status_code=200)

    def test_adding_word_to_dictionary_without_word(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}
        
        sl = StudyingLanguage.objects.create(name='en') 
        word_details = {
            'word': '',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        u = User.objects.create_user(**credentials)
        u.profile.studying_lang = sl
        u.profile.save()

        self.client.login(**credentials)
        
        response = self.client.post('/add_word', word_details)
        failure_message = 'You have not entered any word!'
        self.assertContains(response, text=failure_message, status_code=200)


    def test_redirection_after_successful_adding_word(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}
        
        sl = StudyingLanguage.objects.create(name='en') 
        
        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        u = User.objects.create_user(**credentials)
        
        u.profile.studying_lang = sl
        u.profile.save()

        self.client.login(**credentials)

        response = self.client.post('/add_word', word_details, follow=True)
        path = reverse('words')

        self.assertContains(response, text='successfully added', status_code=200)
        self.assertEqual(path, response.redirect_chain[-1][0])

    def test_trying_to_add_duplicate_word(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}
        
        sl = StudyingLanguage.objects.create(name='en') 
        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        
        almost_the_same_word = {
            'word': 'smallpox',
            'translation': 'натуральная оспа',
            'sentence': 'To Jenner\'s relief James did not catch smallpox.',
        }

        u = User.objects.create_user(**credentials)
        u.profile.studying_lang = sl
        u.profile.save()

        self.client.login(**credentials)
        
        response = self.client.post('/add_word', word_details)
        self.assertEqual(Word.objects.count(), 1)
        response = self.client.post('/add_word', almost_the_same_word)
        self.assertEqual(Word.objects.count(), 1)

    def test_having_related_two_audio_files_to_added_word(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}
        
        sl = StudyingLanguage.objects.create(name='en') 
        
        word_details = {
            'word': 'against',
            'translation': 'против',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        u = User.objects.create_user(**credentials)
        
        u.profile.studying_lang = sl
        u.profile.save()

        self.client.login(**credentials)

        response = self.client.post('/add_word', word_details, follow=True)
        word = Word.objects.last()
        self.assertEqual(word.word, 'against')
        self.assertEqual(GttsAudio.objects.filter(word=word).count(), 2)
    
    def test_having_related_one_audio_file_to_added_word(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}
        
        sl = StudyingLanguage.objects.create(name='en') 
        
        word_details = {
            'word': 'smallpox',
            'translation': 'оспа'
        }

        u = User.objects.create_user(**credentials)
        
        u.profile.studying_lang = sl
        u.profile.save()

        self.client.login(**credentials)

        response = self.client.post('/add_word', word_details, follow=True)
        word = Word.objects.last()
        self.assertEqual(word.word, 'smallpox')
        self.assertEqual(GttsAudio.objects.filter(word=word).count(), 1)



class WordListViewTests(TestCase):
    def test_access_without_authorization(self):
        response = self.client.get('/words', follow=True)
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_without_any_words(self):
        User.objects.create_user(username='pasha', password='1asdfX', email='pasha@gmail.com')
        self.client.login(username='pasha', password='1asdfX')
        response = self.client.get('/words')
        self.assertContains(response, text='You haven\'t added any words', status_code=200)
        self.assertContains(response, text='add word')

    def test_order_of_words(self):
        words = [
            {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'The children were all vaccinated against smallpox.',
                'know_studying_to_native': True,
            },
            {
                'word': 'canteen',
                'translation': 'столовая',
                'sentence': 'they had lunch in the staff canteen',
                'know_native_to_studying': True,
            },
            {
                'word': 'factory',
                'translation': 'фабрика',
                'sentence': 'he works in a clothing factory',
            },
        ]

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }

        sl = StudyingLanguage.objects.create(name='en')

        pasha = User.objects.create_user(**credentials1)
        
        pasha.profile.studying_lang = sl
        pasha.profile.save()

        for word in words:
            Word.objects.create(**word, added_by=pasha, studying_lang=sl)

        self.client.login(**credentials1)

        response = self.client.get('/words')
        self.assertEqual(response.context['words'][0].word, 'factory')


class LearningPageViewTests(TestCase):
    def test_opening_learning_page_without_authorization(self):
        response = self.client.get('/training', follow=True)
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_opening_learning_page_after_authorization_with_words(self):
        smallpox = {
            'word': 'джоб',
            'translation': 'карман',
            'sentence': 'Моите дънки имат два джоба',
        }

        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        
        sl = StudyingLanguage.objects.create(name='bg')
        
        user = User.objects.create_user(**credentials)
        user.profile.studying_lang=sl
        user.profile.save()
        self.client.login(username=credentials['username'], password=credentials['password'])
        
        
        Word.objects.create(**smallpox, added_by=user, studying_lang=sl)
        response = self.client.get('/training')
        self.assertContains(response, status_code=200, text='start (bg-ru)')
        self.assertContains(response, status_code=200, text='start (ru-bg)')
        self.assertNotContains(response, text='username/password')

    def test_opening_learning_page_after_authorization_without_words(self):
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        User.objects.create_user(**credentials)
        self.client.login(username=credentials['username'], password=credentials['password'])
        response = self.client.get('/training')
        self.assertNotContains(response, status_code=200, text='start (en-ru)')
        self.assertNotContains(response, status_code=200, text='start (ru-en)')
        self.assertContains(response, status_code=200, text="To start learning words")
        self.assertNotContains(response, text='username/password')

    def test_know_studying_to_native_card(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        user = User.objects.create_user(**credentials)

        self.client.login(username=credentials['username'], password=credentials['password'])
        sl = StudyingLanguage.objects.create(name='en')
        word = Word.objects.create(**smallpox, added_by=user, studying_lang=sl)
        
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        self.client.login(username=credentials['username'], password=credentials['password'])

        self.client.get('/training')

        response = self.client.get(f'/studying_to_native/{word.id}', follow=True)

        self.assertContains(response, status_code=200, text='smallpox')

    def test_know_native_to_studying_card(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        user = User.objects.create_user(**credentials)

        self.client.login(username=credentials['username'], password=credentials['password'])
        sl = StudyingLanguage.objects.create(name='en')
        word = Word.objects.create(**smallpox, added_by=user, studying_lang=sl)
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        self.client.login(username=credentials['username'], password=credentials['password'])

        self.client.get('/training')

        response = self.client.get(f'/native_to_studying/{word.id}', follow=True)

        self.assertContains(response, status_code=200, text='smallpox')

    def test_drop_word(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        user = User.objects.create_user(**credentials)

        self.client.login(username=credentials['username'], password=credentials['password'])
        sl = StudyingLanguage.objects.create(name='en')
        word = Word.objects.create(**smallpox, added_by=user, studying_lang=sl)
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        self.client.login(username=credentials['username'], password=credentials['password'])
        self.assertEqual(Word.objects.filter(added_by=user).count(), 1)

        self.client.get(f'/words/{word.id}/delete/')

        self.assertEqual(Word.objects.filter(added_by=user).count(), 0)

    def test_drop_unexisting_id_word(self):
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        User.objects.create_user(**credentials)

        self.client.login(username=credentials['username'], password=credentials['password'])

        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        self.client.login(username=credentials['username'], password=credentials['password'])

        response = self.client.get('/words/unexisting_id/delete')
        self.assertEqual(response.status_code, 404)

    def test_trying_to_remove_not_your_word(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        credentials2 = {'username': 'alex', "password": '24safkl', 'email': 'alex@gmail.com'}

        pasha = User.objects.create_user(**credentials1)
        User.objects.create_user(**credentials2)

        self.assertEqual(User.objects.all().count(), 2)
        sl = StudyingLanguage.objects.create(name='en')
        word = Word.objects.create(**smallpox, added_by=pasha, studying_lang=sl)

        self.client.login(username=credentials2['username'], password=credentials2['password'])

        response = self.client.get(f'/words/{word.id}/delete', follow=True)
        self.assertContains(response, status_code=200, text='something went wrong')
        self.assertEqual(Word.objects.all().count(), 1)


class EditWordViewTests(TestCase):
    # before performing each test in this test case we should have an existing user 
    # and the word and we also login
    def setUp(self):
        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        user_credentials = {
            'username': 'pasha', 
            'password': '1asdfX', 
            'email': 'pasha@gmail.com'
        }
        
        # creating a user
        user = User.objects.create_user(**user_credentials)
        
        # creating a "studying language"
        studying_lang = StudyingLanguage.objects.create(name='en')
        
        # binding "studying language" to profile
        user.profile.studying_lang = studying_lang
        user.profile.save()

        # creating a word which will be tested as the updating target
        self.word = Word.objects.create(**word_details, added_by=user, studying_lang=studying_lang)
        
        self.client.login(username=user_credentials['username'], password=user_credentials['password'])

    def test_show_edit_page(self):
        response = self.client.get(f'/words/{self.word.id}/edit', follow=True)
        
        self.assertContains(response, status_code=200, text='smallpox')
        self.assertContains(response, text='оспа')
        self.assertContains(response, 'The children were all vaccinated against smallpox.')
        self.word.delete()

    def test_update_word(self):
        data_to_update = {
                'word': 'smallpoxes', 
                'translation': 'натуральная оспа', 
                'sentence': 'cool smallpoxes'
        }
        # as we've created the word without using AddWord form we don't have any related audios
        self.assertEqual(self.word.gttsaudio_set.count(), 0)

        self.client.post(f'/words/{self.word.id}/edit/', data=data_to_update, follow=True)
        
        word = Word.objects.get(id=self.word.id)
        
        # post request to edit the word uses AddWord form therefore we generate 2 audios ('word' and 'sentence')
        audios = word.gttsaudio_set
        self.assertEqual(audios.count(), 2)
        
        self.assertEqual(audios.filter(use='word').count(), 1)
        self.assertEqual(audios.filter(use='sentence').count(), 1)
        self.assertEqual(word.sentence, 'cool smallpoxes')
        self.assertEqual(word.translation, 'натуральная оспа')
        self.word.delete()

    def test_changing_gtts_audio_after_updating_the_word(self):
        # we perform creating a new word via post request as 
        # only in this case we bind GttsAudio objects to the word.

        new_word = {
                'word': 'box', 
                'translation': 'коробка', 
                'sentence': 'Cats like sitting in box.'
        }
        
        self.client.post('/add_word', new_word)
        
        word = Word.objects.last()
        related_word_audios = word.gttsaudio_set
        
        self.assertEqual(word.word, 'box')
        self.assertEqual(related_word_audios.count(), 2)
        
        initial_word_audio = related_word_audios.filter(use='word')[0]
        initial_sentence_audio = related_word_audios.filter(use='sentence')[0]
        
        data_to_update = {
            'word': 'keyboard',
            'translation': 'клавиатура',
            'sentence': 'I have never used mechanical keyboard.'
        }
        self.client.post(f'/words/{word.id}/edit/', data_to_update)

        updated_word = Word.objects.get(id=word.id)
        
        new_audio_set = updated_word.gttsaudio_set
        
        self.assertEqual(new_audio_set.count(), 2)
        self.assertEqual(updated_word.word, data_to_update['word'])
        self.assertNotEqual(new_audio_set.filter(use='word')[0], initial_word_audio)
        self.assertNotEqual(new_audio_set.filter(use='sentence')[0], initial_sentence_audio)
        word.delete()
        self.word.delete()

    def test_updating_only_sentence_after_updating_the_word(self):
        # we perform creating a new word via post request as 
        # only in this case we bind GttsAudio objects to the word.

        new_word = {
                'word': 'box', 
                'translation': 'коробка', 
                'sentence': 'Cats like sitting in box.'
        }

        self.client.post('/add_word', new_word)
        
        word = Word.objects.last()
        related_word_audios = word.gttsaudio_set
        
        initial_word_audio = related_word_audios.filter(use='word')[0]
        initial_sentence_audio = related_word_audios.filter(use='sentence')[0]
        
        data_to_update = {
            'word': 'box',
            'translation': 'коробочка',
            'sentence': 'Box is very useful tool when you change your lodgings.'
        }

        self.client.post(f'/words/{word.id}/edit/', data_to_update)
        
        updated_word = Word.objects.get(id=word.id)
        current_word_audio = updated_word.gttsaudio_set.filter(use='word')[0]
        current_sentence_audio = updated_word.gttsaudio_set.filter(use='sentence')[0]

        self.assertEqual(updated_word.word, new_word['word'])
        
        self.assertNotEqual(word.sentence, updated_word.sentence)
        self.assertEqual(updated_word.sentence, data_to_update['sentence'])
        self.assertEqual(initial_word_audio, current_word_audio)
        self.assertNotEqual(initial_sentence_audio, current_sentence_audio)

        word.delete()
        self.word.delete()
        



class StudyingToNativeCardViewTests(TestCase):
    def test_knowing_the_word(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        pasha = User.objects.create_user(**credentials1)
        sl = StudyingLanguage.objects.create(name='en')
        word = Word.objects.create(**smallpox, added_by=pasha, studying_lang=sl)

        self.client.login(username=credentials1['username'], password=credentials1['password'])

        self.assertEqual(word.know_studying_to_native, False)

        self.assertEqual(word.know_native_to_studying, False)
        json_data = json.dumps({"id": word.id, "direction": "studying_to_native", "correctness": True})
        self.client.post(f'/studying_to_native/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEqual(word.know_studying_to_native, True)
        self.assertEqual(word.know_native_to_studying, False)

    def test_unknowing_the_word(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
            'know_studying_to_native': True,
            'know_native_to_studying': True,
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        pasha = User.objects.create_user(**credentials1)

        sl = StudyingLanguage.objects.create(name='en')

        word = Word.objects.create(**smallpox, added_by=pasha, studying_lang=sl)

        self.client.login(username=credentials1['username'], password=credentials1['password'])

        json_data = json.dumps({"id": word.id, "direction": "studying_to_native", "correctness": False})
        self.assertEqual(word.know_studying_to_native, True)
        self.assertEqual(word.know_native_to_studying, True)
        self.client.post(f'/studying_to_native/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEqual(word.know_studying_to_native, False)
        self.assertEqual(word.know_native_to_studying, True)

    def test_change_knowing_the_word_by_another_user(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        credentials2 = {'username': 'dima', "password": '1akklk', 'email': 'dima@gmail.com'}
        pasha = User.objects.create_user(**credentials1)
        User.objects.create_user(**credentials2)
        sl = StudyingLanguage.objects.create(name='en')
        word = Word.objects.create(**smallpox, added_by=pasha, studying_lang=sl)

        self.client.login(username=credentials2['username'], password=credentials1['password'])

        self.assertEqual(word.know_studying_to_native, False)

        self.assertEqual(word.know_native_to_studying, False)
        json_data = json.dumps({"id": word.id, "direction": "studying_to_native", "correctness": True})
        self.client.post(f'/studying_to_native/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEqual(word.know_studying_to_native, False)
        self.assertEqual(word.know_native_to_studying, False)


class AccountStatisticsTests(TestCase):
    def test_zero_count_of_words(self):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        pasha = User.objects.create_user(**credentials1)
        pasha = MyUser.objects.get(id=pasha.id)
        self.assertEqual(pasha.words.count(), 0)
        self.assertEqual(pasha.known_words.count(), 0)
        self.assertEqual(pasha.unknown_words.count(), 0)

    def test_count_of_words(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        canteen = {
            'word': 'canteen',
            'translation': 'столовая',
            'sentence': 'they had lunch in the staff canteen',
        }

        factory = {
            'word': 'factory',
            'translation': 'фабрика',
            'sentence': 'he works in a clothing factory',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        pasha = User.objects.create_user(**credentials1)
        sl = StudyingLanguage.objects.create(name='en')
        Word.objects.create(**smallpox, added_by=pasha, studying_lang=sl)
        Word.objects.create(**canteen, added_by=pasha, studying_lang=sl)
        Word.objects.create(**factory, added_by=pasha, studying_lang=sl)

        pasha = MyUser.objects.get(id=pasha.id)
        pasha.profile.studying_lang = sl
        pasha.profile.save()

        self.assertEqual(pasha.words.count(), 3)
        self.assertEqual(pasha.known_words.count(), 0)
        self.assertEqual(pasha.unknown_words.count(), 3)

    def test_count_of_known_words(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        canteen = {
            'word': 'canteen',
            'translation': 'столовая',
            'sentence': 'they had lunch in the staff canteen',
        }

        factory = {
            'word': 'factory',
            'translation': 'фабрика',
            'sentence': 'he works in a clothing factory',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        sl = StudyingLanguage.objects.create(name='en')

        pasha = User.objects.create_user(**credentials1)
        pasha.profile.studying_lang = sl
        pasha.profile.save()
        
        Word.objects.create(**smallpox, added_by=pasha, know_native_to_studying=True, studying_lang=sl)
        Word.objects.create(**canteen, added_by=pasha, know_native_to_studying=True, know_studying_to_native=True, studying_lang=sl)
        Word.objects.create(**factory, added_by=pasha, know_studying_to_native=True, studying_lang=sl)

        pasha = MyUser.objects.get(id=pasha.id)
        self.assertEqual(pasha.words.count(), 3)
        self.assertEqual(pasha.known_words.count(), 1)
        self.assertEqual(pasha.unknown_words.count(), 2)


class ResetProgressTests(TestCase):
    def test_do_not_rest_progress(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
            'know_studying_to_native': True,
            'know_native_to_studying': True,
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }

        pasha = User.objects.create_user(**credentials1)

        sl = StudyingLanguage.objects.create(name='en')

        word = Word.objects.create(**smallpox, added_by=pasha, studying_lang=sl)

        self.client.login(username=credentials1['username'], password=credentials1['password'])

        self.client.get(f'/words/{word.id}/reset/')

        word = Word.objects.get(id=word.id)
        self.assertFalse(word.know_native_to_studying)
        self.assertFalse(word.know_studying_to_native)


class WordIdsTests(TestCase):
    def test_retrieving_all_ids(self):
        words = [
            {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'The children were all vaccinated against smallpox.',
            },
            {
                'word': 'canteen',
                'translation': 'столовая',
                'sentence': 'they had lunch in the staff canteen',
            },
            {
                'word': 'factory',
                'translation': 'фабрика',
                'sentence': 'he works in a clothing factory',
            },
        ]

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }

        pasha = User.objects.create_user(**credentials1)

        sl = StudyingLanguage.objects.create(name='en')

        for word in words:
            Word.objects.create(**word, added_by=pasha, studying_lang=sl)

        self.client.login(**credentials1)

        self.assertEqual(self.client.session.get('word_ids', None), None)

        words_objects = Word.objects.all()
        self.client.get('/')
        session_ids = [word.id for word in words_objects]
        self.assertEqual(len(session_ids), 3)


class TranslateTextTests(TestCase):
    def test_when_no_text(self):
        text, source_lang, target_lang = '', 'ru', 'en'
        tt = TranslateText(source_lang, target_lang)

        result = tt.perform(text)
        self.assertEqual(result, None)

    def test_when_incorrect_source_lang(self):
        text, source_lang, target_lang = 'cat', 'xxx', 'ru'
        tt = TranslateText(source_lang, target_lang)

        with self.assertRaises(ValueError) as context:
            tt.perform(text)
        self.assertEqual((str(context.exception)), 'invalid source language')

    def test_when_incorrect_target_lang(self):
        text, source_lang, target_lang = 'кошка', 'ru', 'xxx'
        tt = TranslateText(source_lang, target_lang)

        with self.assertRaises(ValueError) as context:
            tt.perform(text)
        self.assertEqual((str(context.exception)), 'invalid destination language')

    def test_when_incorrect_source_and_target_lang(self):
        text, source_lang, target_lang = 'кошка', 'yyy', 'xxx'
        tt = TranslateText(source_lang, target_lang)

        with self.assertRaises(ValueError) as context:
            tt.perform(text)
        self.assertEqual((str(context.exception)), 'invalid source language')

    def test_when_no_text_and_incorrect_lang_codes_(self):
        text, source_lang, target_lang = '', 'yyy', 'xxx'
        tt = TranslateText(source_lang, target_lang)

        result = tt.perform(text)
        self.assertEqual(result, None)

    def test_know_native_to_studying_direction(self):
        text, source_lang, target_lang = 'pen', 'en', 'ru'
        tt = TranslateText(source_lang, target_lang)

        result = tt.perform(text)
        self.assertEqual(result, 'ручка')

    def test_know_studying_to_native_direction(self):
        text, source_lang, target_lang = 'карандаш', 'ru', 'en'
        tt = TranslateText(source_lang, target_lang)

        result = tt.perform(text)
        self.assertEqual(result, 'pencil')

    def test_when_invalid_direction(self):
        text, source_lang, target_lang = 'карандаш', 'en', 'ru'
        tt = TranslateText(source_lang, target_lang)

        result = tt.perform(text)
        self.assertNotEqual(result, 'pencil')


class NextListItemTests(TestCase):
    def test_when_empty_list(self):
        lst = []
        current_item = 11

        nli = NextListItem(lst, current_item)
        result = nli.calculate()
        self.assertEqual(result, None)

    def test_when_incorrect_current_item(self):
        lst = [10, 20, 30, 40, 50]
        item = 11

        nli = NextListItem(lst, item)
        result = nli.calculate()
        self.assertEqual(result, None)

    def test_when_current_item_is_last(self):
        lst = [10, 20, 30, 40, 50]
        current_item = 50

        nli = NextListItem(lst, current_item)
        result = nli.calculate()
        self.assertEqual(result, None)

    def test_when_current_item_is_first(self):
        lst = [10, 20, 30, 40, 50]
        current_item = 10

        nli = NextListItem(lst, current_item)
        result = nli.calculate()
        self.assertEqual(result, 20)

    def test_when_current_item_is_the_only_one(self):
        lst = [10,]
        current_item = 10

        nli = NextListItem(lst, current_item)
        result = nli.calculate()
        self.assertEqual(result, None)


class TokenTests(TestCase):
    def test_getting_new_auth_token(self):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }

        pasha = User.objects.create_user(**credentials1)

        self.assertEqual(pasha.id, Token.objects.last().user_id)

    def test_removing_auth_token(self):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }

        pasha = User.objects.create_user(**credentials1)

        self.assertEqual(1, Token.objects.count())

        pasha.delete()

        self.assertEqual(0, Token.objects.count())


class WordViewSetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        credentials2 = {'username': 'vova', "password": '12Sxz_', 'email': 'vova@gmail.com', }
        credentials3 = {'username': 'dima', "password": '1asdfX', 'email': 'dima@gmail.com', }

        sl = StudyingLanguage.objects.create(name='en')

        bg = StudyingLanguage.objects.create(name='bg')
        
        pasha = User.objects.create_user(**credentials1)
        
        pasha.profile.studying_lang = sl
       
        pasha.profile.save()
        
        vova = User.objects.create_user(**credentials2)

        User.objects.create_user(**credentials3)

        words = [
            {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'The children were all vaccinated against smallpox.',
                'studying_lang_id': sl.id
            },
            {
                'word': 'canteen',
                'translation': 'столовая',
                'sentence': 'they had lunch in the staff canteen',
                'studying_lang_id': sl.id
            },
            {
                'word': 'factory',
                'translation': 'фабрика',
                'sentence': 'he works in a clothing factory',
                'studying_lang_id': sl.id
            }, 
            {
                'word': 'слънце',
                'translation': 'солнце',
                'sentence': 'Сутринта слънцето се появи и небото се изчисти.',
                'studying_lang_id': bg.id
            },
            {
                'word': 'сако',
                'translation': 'пиджак',
                'sentence': 'Той облече елегантно сако за интервюто.',
                'studying_lang_id': bg.id
            },
        ]

        word4 = {
                    'word': 'cat',
                    'translation': 'кошка',
                    'sentence': 'it is very difficult to find black cat in black room.',
                    'studying_lang_id': sl.id
                }

        # create 5 words for Pasha
        for word in words:
            Word.objects.create(**word, added_by=pasha)

        # create 1 word for Vova
        Word.objects.create(**word4, added_by=vova)

    def test_retrieving_words_from_api_words(self):
        pasha = User.objects.get(username="pasha")
        auth_token = Token.objects.get(user_id=pasha.id).key

        response = self.client.get('/api/words/', headers={'Authorization': 'Token ' + auth_token})

        results = json.loads(response.content)
        
        # we set studying_lang for pasha is English so only 3 words should be response
        self.assertEqual(results['count'], 3)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'smallpox')
        self.assertEqual(results['results'][1]['word'], 'canteen')
        self.assertEqual(results['results'][2]['word'], 'factory')
    
    def test_retrieving_exact_word_from_api_words(self):
        pasha = User.objects.get(username="pasha")
        auth_token = Token.objects.get(user_id=pasha.id).key

        response = self.client.get('/api/words/?exact_word=canteen', headers={'Authorization': 'Token ' + auth_token})

        results = json.loads(response.content)
        # we set studying_lang for pasha is English so only 3 words should be response
        self.assertEqual(results['count'], 1)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'canteen')

    def test_nothing_retrieving_via_exact_word(self):
        pasha = User.objects.get(username="pasha")
        auth_token = Token.objects.get(user_id=pasha.id).key

        response = self.client.get('/api/words/?exact_word=can', headers={'Authorization': 'Token ' + auth_token})

        results = json.loads(response.content)
        # we set studying_lang for pasha is English so only 3 words should be response
        self.assertEqual(results['count'], 0)
        self.assertEqual(results['next'], None)

    def test_retrieving_filtered_words_from_api_words(self):
        pasha = User.objects.get(username="pasha")

        auth_token = Token.objects.get(user_id=pasha.id).key
        response = self.client.get('/api/words/?word=factory', headers={'Authorization': 'Token ' + auth_token},
                                   follow=True)

        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'factory')
        self.assertEqual(results['results'][0]['translation'], 'фабрика')
        self.assertEqual(results['results'][0]['sentence'], 'he works in a clothing factory')

    def test_filter_words_when_irrelevant_word(self):
        pasha = User.objects.get(username="pasha")

        auth_token = Token.objects.get(user_id=pasha.id).key

        response = self.client.get('/api/words/?word=ffff', headers={'Authorization': 'Token ' + auth_token},
                                   follow=True)
        results = json.loads(response.content)

        self.assertEqual(results['count'], 0)

    def test_filter_words_when_relivant_translation(self):
        pasha = User.objects.get(username="pasha")

        auth_token = Token.objects.get(user_id=pasha.id).key

        response = self.client.get('/api/words/?translation=столовая', headers={'Authorization': 'Token ' + auth_token},
                                   follow=True)
        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['results'][0]['word'], 'canteen')
        self.assertEqual(results['results'][0]['translation'], 'столовая')
        self.assertEqual(results['results'][0]['sentence'], 'they had lunch in the staff canteen')

    def test_filter_words_when_relevant_word_and_translation(self):
        pasha = User.objects.get(username="pasha")

        auth_token = Token.objects.get(user_id=pasha.id).key

        response = self.client.get('/api/words/?translation=столовая&word=cant',
                                   headers={'Authorization': 'Token ' + auth_token}, follow=True)
        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['results'][0]['word'], 'canteen')
        self.assertEqual(results['results'][0]['translation'], 'столовая')
        self.assertEqual(results['results'][0]['sentence'], 'they had lunch in the staff canteen')

    def test_filter_words_when_relevant_word_but_irrelevant_translation(self):
        pasha = User.objects.get(username="pasha")

        auth_token = Token.objects.get(user_id=pasha.id).key

        response = self.client.get('/api/words/?translation= привет&word=cant',
                                   headers={'Authorization': 'Token ' + auth_token}, follow=True)
        results = json.loads(response.content)

        self.assertEqual(results['count'], 0)

    def test_words_from_api_words_when_incorrect_auth_token(self):
        response = self.client.get('/api/words/', headers={'Authorization': 'Token ' + '11111111111111111'})

        self.assertNotContains(response, text='Unauthorized', status_code=401)

    def test_search_by_word_in_words_and_translations(self):
        pasha = User.objects.get(username="pasha")

        auth_token = Token.objects.get(user_id=pasha.id).key
        response = self.client.get('/api/words/?q=to', headers={'Authorization': 'Token ' + auth_token})
        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'factory')

    def test_search_by_translation_in_words_and_translations(self):
        pasha = User.objects.get(username="pasha")

        auth_token = Token.objects.get(user_id=pasha.id).key
        response = self.client.get('/api/words/?q=ка', headers={'Authorization': 'Token ' + auth_token})
        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['translation'], 'фабрика')

    def test_another_search_by_translation_in_words_and_translations(self):
        pasha = User.objects.get(username="pasha")
        
        auth_token = Token.objects.get(user_id=pasha.id).key
        response = self.client.get('/api/words/?q=о', headers={'Authorization': 'Token ' + auth_token})
        results = json.loads(response.content)

        self.assertEqual(results['count'], 2)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['translation'], 'оспа')
        self.assertEqual(results['results'][1]['translation'], 'столовая')

    def test_words_from_api_when_user_has_not_any_words(self):
        dima = User.objects.get(username='dima')

        auth_token = Token.objects.get(user_id=dima.id).key

        response = self.client.get('/api/words/', headers={'Authorization': 'Token ' + auth_token})

        self.assertNotContains(response, text='Success', status_code=200)

        results = json.loads(response.content)

        self.assertEqual(results['count'], 0)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'], [])


    def test_search_only_bulgarian_words(self):
        pasha = User.objects.get(username="pasha")
        
        pasha.profile.studying_lang = StudyingLanguage.objects.last()
        pasha.profile.save()

        auth_token = Token.objects.get(user_id=pasha.id).key
        response = self.client.get('/api/words/?q=о', headers={'Authorization': 'Token ' + auth_token})
        results = json.loads(response.content)

        self.assertEqual(results['count'], 2)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['translation'], 'солнце')
        self.assertEqual(results['results'][1]['word'], 'сако')


    def test_words_from_api_when_user_has_not_any_words(self):
        dima = User.objects.get(username='dima')

        auth_token = Token.objects.get(user_id=dima.id).key

        response = self.client.get('/api/words/', headers={'Authorization': 'Token ' + auth_token})

        self.assertNotContains(response, text='Success', status_code=200)

        results = json.loads(response.content)

        self.assertEqual(results['count'], 0)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'], [])

class StudyingLanguageTests(TestCase):
    def test_successful_creating_language(self):
        self.assertEqual(StudyingLanguage.objects.count(), 0)
        StudyingLanguage.objects.create(name='en')
        self.assertEqual(StudyingLanguage.objects.count(), 1)

    def test_language_can_not_be_empty_string_unique(self):
        with self.assertRaises(ValidationError):
            obj = StudyingLanguage(name='')
            obj.full_clean()

    def test_language_can_not_be_out_of_choice(self):
        with self.assertRaises(ValidationError):
            obj = StudyingLanguage(name='ua')
            obj.full_clean()

    def test_language_must_be_unique(self):
        StudyingLanguage.objects.create(name='bg')

        with self.assertRaises(ValidationError):
            obj = StudyingLanguage(name='bg')
            obj.full_clean()


class ProfileTests(TestCase):
    def test_if_a_new_user_has_profile(self):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
        
        pasha = User.objects.create_user(**credentials1)
        
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(pasha.profile.studying_lang, None)


    def test_no_profile_after_removing_user(self):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        
        
        pasha = User.objects.create_user(**credentials1)
        
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
        
        User.objects.last().delete()
        
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)


    def test_assignment_studying_lang_to_profile(self):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        
        pasha = User.objects.create_user(**credentials1)
        
        self.assertEqual(pasha.profile.studying_lang, None)
        sl = StudyingLanguage.objects.create(name='en')
        pasha.profile.studying_lang = sl
        self.assertEqual(pasha.profile.studying_lang.name, 'en')


class ToggleStudyingLanguageTests(TestCase):
    def test_change_studying_language_for_user(self):
        en = StudyingLanguage.objects.create(name='en')
        bg = StudyingLanguage.objects.create(name='bg')
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        
        pasha = User.objects.create_user(**credentials1)
        
        pasha.profile.studying_lang = bg
        pasha.profile.save()

        self.assertEqual(pasha.profile.studying_lang, bg)

        auth_token = Token.objects.get(user_id=pasha.id).key
        
        client = APIClient()
        response = client.patch('/toggle_lang', {'studying_lang': 'en'}, headers={'Authorization': 'Token ' + auth_token}, format='json')
        self.assertEqual(User.objects.last().profile.studying_lang, en)

    
    def test_set_studying_language_for_user(self):
        en = StudyingLanguage.objects.create(name='en')

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        
        pasha = User.objects.create_user(**credentials1)

        self.assertEqual(pasha.profile.studying_lang, None)

        auth_token = Token.objects.get(user_id=pasha.id).key
        
        client = APIClient()
        response = client.patch('/toggle_lang', {'studying_lang': 'en'}, headers={'Authorization': 'Token ' + auth_token}, format='json')
        self.assertEqual(User.objects.last().profile.studying_lang, en)


    def test_reset_studying_language_for_user(self):
        en = StudyingLanguage.objects.create(name='en')

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        
        pasha = User.objects.create_user(**credentials1)
        
        pasha.profile.studying_lang = en

        self.assertEqual(pasha.profile.studying_lang, en)

        auth_token = Token.objects.get(user_id=pasha.id).key
        
        client = APIClient()
        response = client.patch('/toggle_lang', {'studying_lang': 'None'}, headers={'Authorization': 'Token ' + auth_token}, format='json')
        self.assertEqual(User.objects.last().profile.studying_lang, None)


    def test_trying_to_set_inccorrect_studying_language_for_user(self):
        en = StudyingLanguage.objects.create(name='en')

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        
        pasha = User.objects.create_user(**credentials1)
        
        pasha.profile.studying_lang = en

        self.assertEqual(pasha.profile.studying_lang, en)

        auth_token = Token.objects.get(user_id=pasha.id).key
        
        client = APIClient()
        response = client.patch('/toggle_lang', {'studying_lang': 'bg'}, headers={'Authorization': 'Token ' + auth_token}, format='json')
        self.assertEqual(User.objects.last().profile.studying_lang, None)


    def test_sending_incorrect_data(self):
        en = StudyingLanguage.objects.create(name='en')

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        
        pasha = User.objects.create_user(**credentials1)
        
        pasha.profile.studying_lang = en

        self.assertEqual(pasha.profile.studying_lang, en)

        auth_token = Token.objects.get(user_id=pasha.id).key
        
        client = APIClient()
        response = client.patch('/toggle_lang', {'random': 'data'}, headers={'Authorization': 'Token ' + auth_token}, format='json')
        self.assertEqual(User.objects.last().profile.studying_lang, None)


class TranslateWorldApiTests(TestCase):
    def test_successful_translation_from_bulgarian(self):
        client = APIClient()
        response = client.post('/translate', {'source_lang': 'bg', 'text':'джоб'},  format='json')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['translation'], 'карман')

    def test_successful_translation_from_english(self):
        client = APIClient()
        response = client.post('/translate', {'source_lang': 'en', 'text':'house'},  format='json')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['translation'], 'дом')

    def test_trying_to_translate_empty_str(self):
        client = APIClient()
        response = client.post('/translate', {'source_lang': 'en', 'text':''},  format='json')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['translation'], '') 


class GenerateAudioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='pasha', email='mail@example.com')
        cls.studying_language = StudyingLanguage.objects.create(name='en')

    def test_use_invalid_argument_generating_audio(self):
        '''test ensures that if will not generate audios when we use NOT object of class Word'''
        GenerateAudio(word='sample text').perform()
        self.assertEqual(GttsAudio.objects.count(), 0)


    def test_generating_audios_for_word(self):         
        '''test generating audios for word when we have both "word" and "sentence" and want generate both '''
        word_details = {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'The children were all vaccinated against smallpox.',
            }

        word = Word.objects.create(added_by=self.user, 
                                   studying_lang=self.studying_language, 
                                   **word_details)
        
        GenerateAudio(word=word).perform()
        
        self.assertEqual(GttsAudio.objects.count(), 2)
        word.delete()


    def test_generating_only_one_audio_for_word(self):
        ''' this test ensures we generate only one audio (for "word" attribute), as the "sentence" is empty '''
        word_details = {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': ''
            }

        word = Word.objects.create(added_by=self.user, 
                                   studying_lang=self.studying_language, 
                                   **word_details)

        GenerateAudio(word=word).perform()
        self.assertEqual(GttsAudio.objects.count(), 1)
        word.delete()


    def test_generating_audio_when_the_target_is_word(self):
        ''' this test ensures we generate only one audio (for "word" attribute)'''
        word_details = {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'Smallpox is dangerous disease for humans.'
            }

        word = Word.objects.create(added_by=self.user, 
                                   studying_lang=self.studying_language, 
                                   **word_details)

        GenerateAudio(word=word).perform(target='word')
        
        self.assertEqual(word.gttsaudio_set.count(), 1)
        self.assertEqual(word.gttsaudio_set.first().use, 'word')
        word.delete()
    
    def test_generating_audio_when_the_target_is_sentence(self):
        ''' this test ensures we generate only one audio (for "word" attribute)'''
        word_details = {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'Smallpox is dangerous disease for humans.'
            }

        word = Word.objects.create(added_by=self.user, 
                                   studying_lang=self.studying_language, 
                                   **word_details)

        GenerateAudio(word=word).perform(target='sentence')
        
        self.assertEqual(word.gttsaudio_set.count(), 1)
        self.assertEqual(word.gttsaudio_set.first().use, 'sentence')
        word.delete()
    
