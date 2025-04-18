import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localtime
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.lib.generate_audio import GenerateAudio
from core.lib.next_list_item import NextListItem
from core.lib.remove_file import RemoveFile
from core.lib.translate_text import TranslateText
# from core.lib.remove_from_gcs import RemoveFromGcs
from core.models import GttsAudio, MyUser, Profile, StudyingLanguage, Word
from core.lib.calculate_reset import CalculateReset
from core.lib.update_word_progress import UpdateWordProgress
from core.lib.calculate_user_progress import CalculateUserProgress


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
        form_data = {
            'username': 'pasha',
            'email': 'zihzag@gmail.com',
            'password': '12345678',
            'password_confirmation': '12345678',
        }

        response = self.client.post('/signup', form_data, follow=True)
        text = 'Congratulations! You have successfully registered!'
        u = User.objects.last()
        t = Token.objects.last()
        self.assertEqual(u.email, form_data['email'])
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

        response = self.client.get('/signout', follow=True)
        self.assertContains(response, text='Sign in', status_code=200)


class ProfileViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='pasha', password='1asdfX', email='pasha@gmail.com')

    def test_opening_profile_without_authorization(self):
        response = self.client.get('/profile', follow=True)
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_access_to_account_with_authorization(self):
        self.client.login(username='pasha', password='1asdfX')

        response = self.client.get('/profile', follow=True)

        self.assertContains(response, text='pasha', status_code=200)
        self.assertContains(response, text='pasha@gmail.com', status_code=200)
        self.assertContains(response, text=localtime().date())


class AddWordViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credentials = {'username': 'pasha', 'password': '1asdfX'}

        cls.sl = StudyingLanguage.objects.create(name='en')

        cls.word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        u = User.objects.create_user(**cls.credentials)
        u.profile.studying_lang = cls.sl
        u.profile.save()

    def setUp(self):
        self.client.login(**self.credentials)
    
    # this function removes all unnecessary gTTS files which are saved in the media/ directory during tests
    def tearDown(self):
        files_to_remove = GttsAudio.objects.all().values_list('audio_name', flat=True)

        for filename in files_to_remove:
            if filename:
                RemoveFile(filename).perform()
                # RemoveFromGcs().perform(filename)

    def test_access_to_form_for_not_authorized_user(self):
        self.client.logout()
        response = self.client.get('/add_word', follow=True)
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_access_to_form_for_authorized_user(self):
        response = self.client.get('/add_word')
        self.assertContains(response, text='word', status_code=200)
        self.assertContains(response, text='translation')
        self.assertContains(response, text='sentence')
        self.assertContains(response, text='add')

    def test_adding_word_to_dictionary(self):
        response = self.client.post('/add_word', self.word_details, follow=True)
        success_message = f'&quot;{self.word_details["word"]}&quot; was successfully added to your learn list!'
        words = Word.objects.all()
        
        self.assertEqual(words.count(), 1)
        self.assertEqual(GttsAudio.objects.filter(word=words[0]).count(), 2)
        self.assertContains(response, text=success_message, status_code=200)

    def test_adding_word_to_dictionary_without_translation(self):
        response = self.client.post('/add_word', {**self.word_details, 'translation': ''})
        failure_message = f'You have not added translation for {self.word_details["word"]}!'
        self.assertContains(response, text=failure_message, status_code=200)

    def test_adding_word_to_dictionary_without_sentence(self):
        word_details = {**self.word_details, 'sentence': ''}

        response = self.client.post('/add_word', word_details, follow=True)

        success_message = f'&quot;{word_details['word']}&quot; was successfully added to your learn list!'
        
        words = Word.objects.filter(word=word_details['word'])
        
        self.assertEqual(words.count(), 1)
        self.assertEqual(GttsAudio.objects.filter(word=words[0]).count(), 1)
        self.assertContains(response, text=success_message, status_code=200)

    def test_adding_word_to_dictionary_without_word(self):
        response = self.client.post('/add_word', {**self.word_details, 'word': ''})
        failure_message = 'You have not entered any word!'
        self.assertContains(response, text=failure_message, status_code=200)


    def test_redirection_after_successful_adding_word(self):
        response = self.client.post('/add_word', self.word_details, follow=True)
        path = reverse('add_word')

        self.assertContains(response, text='successfully added', status_code=200)
        self.assertEqual(path, response.redirect_chain[-1][0])

    def test_trying_to_add_duplicate_word(self):
        almost_the_same_word = {
            'word': 'smallpox',
            'translation': 'натуральная оспа',
            'sentence': 'To Jenner\'s relief James did not catch smallpox.',
        }

        self.client.post('/add_word', self.word_details)
        self.assertEqual(Word.objects.count(), 1)

        self.client.post('/add_word', almost_the_same_word)
        self.assertEqual(Word.objects.count(), 1)


class WordListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sl = StudyingLanguage.objects.create(name='en')
        cls.credentials = {'username': 'pasha', 'email': 'mail@example.com', 'password':'1asdfX'}
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.profile.studying_lang = cls.sl
        cls.user.profile.save()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_access_without_authorization(self):
        self.client.logout()
        response = self.client.get('/words', follow=True)
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_without_any_words(self):
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

        for word in words:
            Word.objects.create(**word, added_by=self.user, studying_lang=self.sl)

        response = self.client.get('/words')
        self.assertEqual(response.context['words'][0].word, 'factory')


class ExercisesPageViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        
        cls.user = User.objects.create_user(**cls.credentials)
        cls.bg = StudyingLanguage.objects.create(name='bg')
        cls.en = StudyingLanguage.objects.create(name='en')

    def setUp(self):
        self.client.login(**self.credentials) 

    def test_opening_learning_page_without_authorization(self):
        self.client.logout()
        response = self.client.get('/exercises', follow=True)
        
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_opening_learning_page_after_authorization_with_words(self):
        self.user.profile.studying_lang = self.bg
        self.user.profile.save()

        bulgarian_word = {
            'word': 'джоб',
            'translation': 'карман',
            'sentence': 'Моите дънки имат два джоба',
        }
        
        Word.objects.create(**bulgarian_word, added_by=self.user, studying_lang=self.bg)
        response = self.client.get('/exercises')
        
        self.assertContains(response, status_code=200, text='start (bg-ru)')
        self.assertContains(response, status_code=200, text='start (ru-bg)')
        self.assertNotContains(response, text='username/password')

    def test_opening_learning_page_after_authorization_without_words(self):
        response = self.client.get('/exercises')
        
        self.assertNotContains(response, status_code=200, text='start (bg-ru)')
        self.assertNotContains(response, status_code=200, text='start (ru-bg)')
        self.assertContains(response, status_code=200, text="To start learning words")
        self.assertNotContains(response, text='username/password')

    def test_know_studying_to_native_card(self):
        english_word = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        word = Word.objects.create(**english_word, added_by=self.user, studying_lang=self.en)
        self.client.get('/exercises')
        response = self.client.get(f'/studying_to_native/{word.id}', follow=True)

        self.assertContains(response, status_code=200, text='smallpox')

    def test_know_native_to_studying_card(self):
        english_word = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        word = Word.objects.create(**english_word, added_by=self.user, studying_lang=self.en)
        self.client.get('/exercises')
        response = self.client.get(f'/native_to_studying/{word.id}', follow=True)

        self.assertContains(response, status_code=200, text='smallpox')


class DeleteWordViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        cls.user = User.objects.create_user(**cls.credentials)
        en = StudyingLanguage.objects.create(name='en')
        cls.word = Word.objects.create(**smallpox, added_by=cls.user, studying_lang=en)
    
    def setUp(self):
        self.client.login(**self.credentials)
        
    def test_successful_removing_word(self):
        self.assertEqual(Word.objects.filter(added_by=self.user).count(), 1)
        response = self.client.get(f'/words/{self.word.id}/delete/', follow=True)
        message = f'Congratulations! You have successfully deleted &quot;{self.word.word}&quot;' 
        self.assertContains(response, text=message, status_code=200)
        self.assertEqual(Word.objects.filter(added_by=self.user).count(), 0)

    def test_drop_unexisting_id_word(self):
        response = self.client.get('/words/unexisting_id/delete')
        self.assertEqual(response.status_code, 404)

    def test_trying_to_remove_not_your_word(self):
        credentials2 = {'username': 'alex', "password": '24safkl', 'email': 'alex@gmail.com'}
        User.objects.create_user(**credentials2)
        self.assertEqual(User.objects.all().count(), 2)

        self.client.logout()
        self.client.login(**credentials2)

        response = self.client.get(f'/words/{self.word.id}/delete', follow=True)
        self.assertContains(response, status_code=200, text='something went wrong')
        self.assertEqual(Word.objects.all().count(), 1)


class EditWordViewTests(TestCase):
    # before performing each test in this test case we should have an existing user 
    # and the word and we also login
    @classmethod
    def setUpTestData(cls):
        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        cls.credentials = {
            'username': 'pasha', 
            'password': '1asdfX', 
            'email': 'pasha@gmail.com'
        }
        # creating a user
        user = User.objects.create_user(**cls.credentials)
        # creating a "studying language"
        studying_lang = StudyingLanguage.objects.create(name='en')
        
        # binding "studying language" to profile
        user.profile.studying_lang = studying_lang
        user.profile.save()

        # creating a word which will be tested as the updating target
        cls.word = Word.objects.create(**word_details, added_by=user, studying_lang=studying_lang)
        
    def setUp(self):
        self.client.login(**self.credentials)

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
    @classmethod
    def setUpTestData(cls):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        cls.credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        # create user
        pasha = User.objects.create_user(**cls.credentials1)
        en = StudyingLanguage.objects.create(name='en')
        # create word 
        cls.word = Word.objects.create(**smallpox, added_by=pasha, studying_lang=en)

    def setUp(self):
        self.client.login(**self.credentials1)

    def test_initial_knowing_of_new_word(self):
        # any new word, by default, must be fully unknown
        self.assertFalse(self.word.know_studying_to_native)
        self.assertFalse(self.word.know_native_to_studying)

    def test_knowing_the_word(self):
        studying_params = {"id": self.word.id, "direction": "studying_to_native", "correctness": True}

        json_data = json.dumps(studying_params)
        self.client.post(f'/studying_to_native/{self.word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertTrue(word.know_studying_to_native)
        self.assertFalse(word.know_native_to_studying)

    def test_unknowing_the_word(self):
        self.word.know_studying_to_native=True
        self.word.know_native_to_studying=True
        self.word.save()

        json_data = json.dumps({"id": self.word.id, "direction": "studying_to_native", "correctness": False})
        self.client.post(f'/studying_to_native/{self.word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertFalse(word.know_studying_to_native)
        self.assertTrue(word.know_native_to_studying)

    def test_change_knowing_the_word_by_another_user(self):
        self.client.logout()
        credentials2 = {'username': 'dima', "password": '1akklk', 'email': 'dima@gmail.com'}
        User.objects.create_user(**credentials2)

        self.client.login(**credentials2)

        json_data = json.dumps({"id": self.word.id, "direction": "studying_to_native", "correctness": True})
        self.client.post(f'/studying_to_native/{self.word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertFalse(word.know_studying_to_native)
        self.assertFalse(word.know_native_to_studying)


class AccountStatisticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        cls.pasha = User.objects.create_user(**credentials1)
        cls.en = StudyingLanguage.objects.create(name='en')
        cls.pasha.profile.studying_lang = cls.en
        cls.pasha.profile.save()
        cls.account = MyUser.objects.get(id=cls.pasha.id)

    def test_zero_count_of_words(self):
        self.assertEqual(self.account.words.count(), 0)
        self.assertEqual(self.account.known_words.count(), 0)
        self.assertEqual(self.account.unknown_words.count(), 0)

    def test_count_of_words(self):
        english_words = [{
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }, {
            'word': 'canteen',
            'translation': 'столовая',
            'sentence': 'they had lunch in the staff canteen',
        }, {
            'word': 'factory',
            'translation': 'фабрика',
            'sentence': 'he works in a clothing factory',
        }]

        for word in english_words:
            Word.objects.create(**word, added_by=self.pasha, studying_lang=self.en)

        self.assertEqual(self.account.words.count(), 3)
        self.assertEqual(self.account.known_words.count(), 0)
        self.assertEqual(self.account.unknown_words.count(), 3)

    def test_count_of_known_words(self):
        english_words = [{
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
            'know_native_to_studying': True
        }, {
            'word': 'canteen',
            'translation': 'столовая',
            'sentence': 'they had lunch in the staff canteen',
            'know_native_to_studying': True,
            'know_studying_to_native': True
        }, {
            'word': 'factory',
            'translation': 'фабрика',
            'sentence': 'he works in a clothing factory',
            'know_studying_to_native': True
        }]

        for word in english_words:
            Word.objects.create(**word, added_by=self.pasha, studying_lang=self.en)

        self.assertEqual(self.account.words.count(), 3)
        self.assertEqual(self.account.known_words.count(), 1)
        self.assertEqual(self.account.unknown_words.count(), 2)


class ResetProgressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
            'know_studying_to_native': True,
            'know_native_to_studying': True,
        }

        cls.credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        pasha = User.objects.create_user(**cls.credentials1)
        en = StudyingLanguage.objects.create(name='en')
        cls.word = Word.objects.create(**smallpox, added_by=pasha, studying_lang=en)
    
    def setUp(self):
        self.client.login(**self.credentials1)
    
    def test_rest_progress(self):
        self.client.get(f'/words/{self.word.id}/reset/')
        word = Word.objects.get(id=self.word.id)

        self.assertFalse(word.know_native_to_studying)
        self.assertFalse(word.know_studying_to_native)

    def test_do_not_rest_progress(self):
        self.client.get(f'/words/invalid_id/reset/')
        word = Word.objects.get(id=self.word.id)
        
        self.assertTrue(word.know_native_to_studying)
        self.assertTrue(word.know_studying_to_native)

    def test_reset_word_method(self):
        word = Word.objects.get(id=self.word.id)
        word.times_in_row = 2
        word.stage = 'month'
        word.save()

        self.assertTrue(word.know_native_to_studying)
        self.assertTrue(word.know_studying_to_native)
        word.reset_progress()
        self.assertEqual(word.times_in_row, 0)
        self.assertEqual(word.stage, 'day')
        self.assertFalse(word.know_native_to_studying)
        self.assertFalse(word.know_studying_to_native)



class WordIdsTests(TestCase):
    def setUp(self):
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

    def test_retrieving_all_ids(self):
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
    @classmethod
    def setUp(cls):
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        cls.pasha = User.objects.create_user(**credentials)

    def test_a_user_has_auth_token(self):
        self.assertEqual(self.pasha.id, Token.objects.last().user_id)

    def test_removing_auth_token(self):
        self.pasha.delete()
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
        cls.pasha_token = Token.objects.get(user=pasha).key
        
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
        response = self.client.get('/api/words/', headers={'Authorization': 'Token ' + self.pasha_token})

        results = json.loads(response.content)
        
        # we set studying_lang for pasha is English so only 3 words should be response
        self.assertEqual(results['count'], 3)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'smallpox')
        self.assertEqual(results['results'][1]['word'], 'canteen')
        self.assertEqual(results['results'][2]['word'], 'factory')
    
    def test_retrieving_exact_word_from_api_words(self):
        response = self.client.get('/api/words/?exact_word=canteen', headers={'Authorization': 'Token ' + self.pasha_token})

        results = json.loads(response.content)
        # we set studying_lang for pasha is English so only 3 words should be response
        self.assertEqual(results['count'], 1)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'canteen')

    def test_nothing_retrieving_via_exact_word(self):
        response = self.client.get('/api/words/?exact_word=can', headers={'Authorization': 'Token ' + self.pasha_token})

        results = json.loads(response.content)
        # we set studying_lang for pasha is English so only 3 words should be response
        self.assertEqual(results['count'], 0)
        self.assertEqual(results['next'], None)

    def test_retrieving_filtered_words_from_api_words(self):
        response = self.client.get('/api/words/?word=factory', headers={'Authorization': 'Token ' + self.pasha_token},
                                   follow=True)

        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'factory')
        self.assertEqual(results['results'][0]['translation'], 'фабрика')
        self.assertEqual(results['results'][0]['sentence'], 'he works in a clothing factory')

    def test_filter_words_when_irrelevant_word(self):
        response = self.client.get('/api/words/?word=ffff', headers={'Authorization': 'Token ' + self.pasha_token},
                                   follow=True)
        results = json.loads(response.content)

        self.assertEqual(results['count'], 0)

    def test_filter_words_when_relivant_translation(self):
        response = self.client.get('/api/words/?translation=столовая', headers={'Authorization': 'Token ' + self.pasha_token},
                                   follow=True)
        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['results'][0]['word'], 'canteen')
        self.assertEqual(results['results'][0]['translation'], 'столовая')
        self.assertEqual(results['results'][0]['sentence'], 'they had lunch in the staff canteen')

    def test_filter_words_when_relevant_word_and_translation(self):
        response = self.client.get('/api/words/?translation=столовая&word=cant',
                                   headers={'Authorization': 'Token ' + self.pasha_token}, follow=True)
        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['results'][0]['word'], 'canteen')
        self.assertEqual(results['results'][0]['translation'], 'столовая')
        self.assertEqual(results['results'][0]['sentence'], 'they had lunch in the staff canteen')

    def test_filter_words_when_relevant_word_but_irrelevant_translation(self):
        response = self.client.get('/api/words/?translation= привет&word=cant',
                                   headers={'Authorization': 'Token ' + self.pasha_token}, follow=True)
        results = json.loads(response.content)

        self.assertEqual(results['count'], 0)

    def test_words_from_api_words_when_incorrect_auth_token(self):
        response = self.client.get('/api/words/', headers={'Authorization': 'Token ' + '11111111111111111'})

        self.assertNotContains(response, text='Unauthorized', status_code=401)

    def test_search_by_word_in_words_and_translations(self):
        response = self.client.get('/api/words/?q=to', headers={'Authorization': 'Token ' + self.pasha_token})
        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'factory')

    def test_search_by_translation_in_words_and_translations(self):
        response = self.client.get('/api/words/?q=ка', headers={'Authorization': 'Token ' + self.pasha_token})
        results = json.loads(response.content)

        self.assertEqual(results['count'], 1)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['translation'], 'фабрика')

    def test_another_search_by_translation_in_words_and_translations(self):
        response = self.client.get('/api/words/?q=о', headers={'Authorization': 'Token ' + self.pasha_token})
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

        response = self.client.get('/api/words/?q=о', headers={'Authorization': 'Token ' + self.pasha_token})
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
    @classmethod
    def setUpTestData(cls):
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        cls.pasha = User.objects.create_user(**credentials)

    def test_if_a_new_user_has_profile(self):
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
        self.assertIsNone(self.pasha.profile.studying_lang)


    def test_no_profile_after_removing_user(self):
        User.objects.last().delete()
        
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)


    def test_assignment_studying_lang_to_profile(self):
        self.assertIsNone(self.pasha.profile.studying_lang)
        
        en = StudyingLanguage.objects.create(name='en')
        
        self.pasha.profile.studying_lang = en
        self.pasha.profile.save()
        
        profile = User.objects.last().profile
        
        self.assertEqual(profile.studying_lang.name, 'en')


class ToggleStudyingLanguageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.en = StudyingLanguage.objects.create(name='en')
        cls.bg = StudyingLanguage.objects.create(name='bg')
        
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }
        cls.pasha = User.objects.create_user(**credentials)
        cls.token = Token.objects.get(user_id=cls.pasha.id).key

    def setUp(self):
        self.client = APIClient()
    
    def test_new_user_has_not_studying_lang(self):
        self.assertIsNone(self.pasha.profile.studying_lang)

    def test_change_studying_language_for_user(self):
        self.pasha.profile.studying_lang = self.bg
        self.pasha.profile.save()
        
        self.client.patch('/toggle_lang', {'studying_lang': 'en'}, 
                     headers={'Authorization': 'Token ' + self.token}, format='json')
        self.assertEqual(User.objects.last().profile.studying_lang, self.en)
    
    def test_set_studying_language_for_user(self):
        self.client.patch('/toggle_lang', {'studying_lang': 'en'}, 
                     headers={'Authorization': 'Token ' + self.token}, format='json')
        self.assertEqual(User.objects.last().profile.studying_lang, self.en)


    def test_reset_studying_language_for_user(self):
        self.client.patch('/toggle_lang', {'studying_lang': 'None'}, 
                     headers={'Authorization': 'Token ' + self.token}, format='json')
        self.assertIsNone(User.objects.last().profile.studying_lang)


    def test_trying_to_set_inccorrect_studying_language_for_user(self):
        self.client.patch('/toggle_lang', {'studying_lang': 'yy'}, 
                                headers={'Authorization': 'Token ' + self.token}, format='json')
        self.assertIsNone(User.objects.last().profile.studying_lang)


    def test_sending_incorrect_data(self):
        self.client.patch('/toggle_lang', {'random': 'data'}, 
                                headers={'Authorization': 'Token ' + self.token}, format='json')
        self.assertIsNone(User.objects.last().profile.studying_lang)


class TranslateWorldApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_successful_translation_from_bulgarian(self):
        response = self.client.post('/translate', {'source_lang': 'bg', 'text':'джоб'},  format='json')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['translation'], 'карман')

    def test_successful_translation_from_english(self):
        response = self.client.post('/translate', {'source_lang': 'en', 'text':'house'},  format='json')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['translation'], 'дом')

    def test_trying_to_translate_empty_str(self):
        response = self.client.post('/translate', {'source_lang': 'en', 'text':''},  format='json')
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


class AvailableLanguagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(username='pasha', email='pashaibratanov@gmail.com')
        
        cls.en = StudyingLanguage.objects.create(name='en')
        cls.bg = StudyingLanguage.objects.create(name='bg')

    def test_user_has_not_studying_language_test(self):
        self.assertIsNone(self.user.profile.studying_lang)
        
        available_languages = self.user.profile.available_languages
        
        self.assertEqual(len(available_languages), 2)
        self.assertIn(self.en, available_languages)
        self.assertIn(self.bg, available_languages)


    def test_user_has_studying_language(self):
        self.user.profile.studying_lang = self.en
        self.user.profile.save()

        self.assertEqual(self.user.profile.studying_lang, self.en)
        
        available_languages = self.user.profile.available_languages
        
        self.assertEqual(len(available_languages), 1)
        self.assertIn(self.bg, available_languages)
        self.assertNotIn(self.en, available_languages)


class CalculateResetTests(TestCase):
    def test_calc_reset_for_new_word(self):
        stage = 'day'
        times_in_row = 0

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 1)
        self.assertEqual(result.stage, 'day')


    def test_calc_reset_for_daily_word(self):
        stage = 'day'
        times_in_row = 3

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 7)
        self.assertEqual(result.stage, 'week')


    def test_calc_reset_for_first_weekly_word(self):
        stage = 'week'
        times_in_row = 0

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 7)
        self.assertEqual(result.stage, 'week')

        
    def test_calc_reset_for_weekly_word(self):
        stage = 'week'
        times_in_row = 3

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 30)
        self.assertEqual(result.stage, 'month')

    def test_calc_reset_for_first_month_word(self):
        stage = 'month'
        times_in_row = 0

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 30)
        self.assertEqual(result.stage, 'month')

    def test_calc_reset_for_month_word(self):
        stage = 'month'
        times_in_row = 3

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 90)
        self.assertEqual(result.stage, 'three_month')
        
    def test_calc_reset_for_first_three_month_word(self):
        stage = 'three_month'
        times_in_row = 0

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 90)
        self.assertEqual(result.stage, 'three_month')


    def test_calc_reset_for_three_month_word(self):
        stage = 'three_month'
        times_in_row = 3

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 180)
        self.assertEqual(result.stage, 'half_year')

    def test_calc_reset_first_half_year_word(self):
        stage = 'half_year'
        times_in_row = 0

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 180)
        self.assertEqual(result.stage, 'half_year')

    def test_calc_reset_well_known_word(self):
        stage = 'half_year'
        times_in_row = 3

        result = CalculateReset(stage=stage, times_in_row=times_in_row).perform()
        
        self.assertEqual(result.reset_in_days, 180)
        self.assertEqual(result.stage, 'half_year')

    


class UpdateWordProgressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='pasha', email='mail@example.com')
        cls.studying_language = StudyingLanguage.objects.create(name='en')
        word_details = {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'Smallpox is dangerous disease for humans.'
            }

        cls.word = Word.objects.create(added_by=cls.user, 
                                   studying_lang=cls.studying_language, 
                                   **word_details)


    def test_change_progress_for_newly_word(self):
        self.assertEqual(self.word.stage, 'day')
        self.assertEqual(self.word.times_in_row, 0)
        
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'day')
        self.assertEqual(word.times_in_row, 1)

    def test_change_reset_date_second_time_day_word(self):
        self.word.stage = 'day'
        self.word.times_in_row = 1
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'day')
        self.assertEqual(word.times_in_row, 2)

    
    def test_change_reset_date_third_time_day_word(self):
        self.word.stage = 'day'
        self.word.times_in_row = 2
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'day')
        self.assertEqual(word.times_in_row, 3)


    def test_change_reset_date_fourth_day_word(self):
        self.word.stage = 'day'
        self.word.times_in_row = 3
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'week')
        self.assertEqual(word.times_in_row, 0)

    def test_change_reset_date_first_week_word(self):
        self.word.stage = 'week'
        self.word.times_in_row = 0
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'week')
        self.assertEqual(word.times_in_row, 1)

    def test_change_reset_date_third_week_word(self):
        self.word.stage = 'week'
        self.word.times_in_row = 3
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'month')
        self.assertEqual(word.times_in_row, 0)


    def test_change_reset_date_first_month_word(self):
        self.word.stage = 'month'
        self.word.times_in_row = 0
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'month')
        self.assertEqual(word.times_in_row, 1)

    def test_change_reset_date_third_month_word(self):
        self.word.stage = 'month'
        self.word.times_in_row = 3
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'three_month')
        self.assertEqual(word.times_in_row, 0)


    def test_change_reset_date_first_three_month_word(self):
        self.word.stage = 'three_month'
        self.word.times_in_row = 0
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'three_month')
        self.assertEqual(word.times_in_row, 1)

    def test_change_reset_date_third_three_month_word(self):
        self.word.stage = 'three_month'
        self.word.times_in_row = 3
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'half_year')
        self.assertEqual(word.times_in_row, 0)

    def test_change_reset_date_firsth_half_year_word(self):
        self.word.stage = 'half_year'
        self.word.times_in_row = 0
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'half_year')
        self.assertEqual(word.times_in_row, 1)

    def test_change_reset_date_fifth_half_year_word(self):
        self.word.stage = 'half_year'
        self.word.times_in_row = 5
        
        self.word.save()
        UpdateWordProgress(self.word).perform()
        
        word = Word.objects.last()

        self.assertEqual(word.stage, 'half_year')
        self.assertEqual(word.times_in_row, 6)


class CalculateProgressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='pasha', email='pasha@mail.com')
        cls.dima = User.objects.create(username='dima', email='dima@mail.com')
        cls.en = StudyingLanguage.objects.create(name='en')
        cls.bg = StudyingLanguage.objects.create(name='bg')

    def test_user_progress_without_any_words(self):
        calc = CalculateUserProgress(user=self.user, studying_lang=self.en)
        self.assertEqual(calc.perform('total'), None)
        self.assertEqual(calc.perform('native_to_studying'), None)
        self.assertEqual(calc.perform('studying_to_native'), None)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).native_to_studying(), None)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).studying_to_native(), None)



    def test_user_progress_with_one_new_word(self):
        word_details = {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'Smallpox is dangerous disease for humans.'
            }

        word = Word.objects.create(added_by=self.user, 
                                   studying_lang=self.en, 
                                   **word_details)
        
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).total(), 0)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).native_to_studying(), 0)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).studying_to_native(), 0)
        calc = CalculateUserProgress(user=self.user, studying_lang=self.en)
        self.assertEqual(calc.perform('total'), 0)
        self.assertEqual(calc.perform('native_to_studying'), 0)
        self.assertEqual(calc.perform('studying_to_native'), 0)
        word.delete()

    def test_user_progress_with_one_studyied_word(self):
        word_details = {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'Smallpox is dangerous disease for humans.'
            }

        word = Word.objects.create(added_by=self.user, 
                                   studying_lang=self.en, 
                                   know_native_to_studying=True,
                                know_studying_to_native=True,
                                   **word_details)
        
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).total(), 100)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).native_to_studying(), 100)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).studying_to_native(), 100)
        calc = CalculateUserProgress(user=self.user, studying_lang=self.en)
        self.assertEqual(calc.perform('total'), 100)
        self.assertEqual(calc.perform('native_to_studying'), 100)
        self.assertEqual(calc.perform('studying_to_native'), 100)
        word.delete()

    def test_user_progress_with_one_studyied_and_one_unstudyied_word(self):
        words = [
            {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'Smallpox is dangerous disease for humans.',
                'know_native_to_studying': True,
                'know_studying_to_native': True
            },
            {
                'word': 'cat',
                'translation': 'кошка',
                'sentence': 'it is very difficult to find black cat in black room.'
            },
        ]

        for word in words:
            Word.objects.create(added_by=self.user, studying_lang=self.en, **word)
        
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).total(), 50)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).native_to_studying(), 50)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).studying_to_native(), 50)
        calc = CalculateUserProgress(user=self.user, studying_lang=self.en)
        self.assertEqual(calc.perform('total'), 50)
        self.assertEqual(calc.perform('native_to_studying'), 50)
        self.assertEqual(calc.perform('studying_to_native'), 50)


    def test_user_progress_with_one_studyied_and_two_unstudyied_word(self):
        words = [
            {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'Smallpox is dangerous disease for humans.',
                'know_native_to_studying': True,
                'know_studying_to_native': True
            },
            {
                'word': 'cat',
                'translation': 'кошка',
                'sentence': 'it is very difficult to find black cat in black room.'
            },
            {
                'word': 'tree',
                'translation': 'дерево',
                'sentence': 'the tree is very tall'
            },
        ]

        for word in words:
            Word.objects.create(added_by=self.user, studying_lang=self.en, **word)
        
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).total(), 33.33)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).native_to_studying(), 33.33)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).studying_to_native(), 33.33)
        calc = CalculateUserProgress(user=self.user, studying_lang=self.en)
        self.assertEqual(calc.perform('total'), 33.33)
        self.assertEqual(calc.perform('native_to_studying'), 33.33)
        self.assertEqual(calc.perform('studying_to_native'), 33.33)


    def test_user_progress_with_one_studyied_one_partly_studyied_and_one_unstudyied_word(self):
        words = [
            {
                'word': 'smallpox',
                'translation': 'оспа',
                'sentence': 'Smallpox is dangerous disease for humans.',
                'know_native_to_studying': True,
                'know_studying_to_native': True
            },
            {
                'word': 'cat',
                'translation': 'кошка',
                'sentence': 'it is very difficult to find black cat in black room.',
                'know_native_to_studying': True
            },
            {
                'word': 'tree',
                'translation': 'дерево',
                'sentence': 'the tree is very tall'
            },
        ]

        for word in words:
            Word.objects.create(added_by=self.user, studying_lang=self.en, **word)
        
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).total(), 33.33)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).native_to_studying(), 66.67)
        # self.assertEqual(CalculateUserProgress(user=self.user, studying_lang=self.en).studying_to_native(), 33.33)
        calc = CalculateUserProgress(user=self.user, studying_lang=self.en)
        self.assertEqual(calc.perform('total'), 33.33)
        self.assertEqual(calc.perform('native_to_studying'), 66.67)
        self.assertEqual(calc.perform('studying_to_native'), 33.33)
        