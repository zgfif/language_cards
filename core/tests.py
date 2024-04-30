import json
from django.utils.timezone import localtime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from core.lib.remove_file import RemoveFile
from core.lib.remove_from_gcs import RemoveFromGcs
from core.models import Word, MyUser, GttsAudio
from core.lib.translate_text import TranslateText
from core.lib.next_list_item import NextListItem


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
                RemoveFromGcs().perform(filename)

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

        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        User.objects.create_user(**credentials)
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

        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': '',
        }
        User.objects.create_user(**credentials)
        self.client.login(**credentials)

        response = self.client.post('/add_word', word_details, follow=True)
        success_message = f'{word_details["word"]} was successfully added to your learn list!'
        self.assertEqual(Word.objects.filter(word=word_details['word']).count(), 1)
        self.assertContains(response, text=success_message, status_code=200)

    def test_adding_word_to_dictionary_without_word(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}

        word_details = {
            'word': '',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        User.objects.create_user(**credentials)
        self.client.login(**credentials)

        response = self.client.post('/add_word', word_details)
        failure_message = 'You have not entered any word!'
        self.assertContains(response, text=failure_message, status_code=200)

    def test_redirection_after_successful_adding_word(self):
        credentials = {'username': 'pasha', 'password': '1asdfX'}

        word_details = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        User.objects.create_user(**credentials)
        self.client.login(**credentials)

        response = self.client.post('/add_word', word_details, follow=True)
        path = reverse('words')

        self.assertContains(response, text='successfully added', status_code=200)
        self.assertEqual(path, response.redirect_chain[-1][0])


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
                'en_ru': True,
            },
            {
                'word': 'canteen',
                'translation': 'столовая',
                'sentence': 'they had lunch in the staff canteen',
                'ru_en': True,
            },
            {
                'word': 'factory',
                'translation': 'фабрика',
                'sentence': 'he works in a clothing factory',
            },
        ]

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }

        pasha = User.objects.create_user(**credentials1)

        for word in words:
            Word.objects.create(**word, added_by=pasha)

        Word.objects.first().is_known()
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
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        user = User.objects.create_user(**credentials)
        self.client.login(username=credentials['username'], password=credentials['password'])
        Word.objects.create(**smallpox, added_by=user)
        response = self.client.get('/training')
        self.assertContains(response, status_code=200, text='start (en-ru)')
        self.assertContains(response, status_code=200, text='start (ru-en)')
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

    def test_en_ru_card(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        user = User.objects.create_user(**credentials)

        self.client.login(username=credentials['username'], password=credentials['password'])
        word = Word.objects.create(**smallpox, added_by=user)
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        self.client.login(username=credentials['username'], password=credentials['password'])

        self.client.get('/training')

        response = self.client.get(f'/learn_word/en-ru/{word.id}', follow=True)

        self.assertContains(response, status_code=200, text='smallpox')

    def test_ru_en_card(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        user = User.objects.create_user(**credentials)

        self.client.login(username=credentials['username'], password=credentials['password'])
        word = Word.objects.create(**smallpox, added_by=user)
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        self.client.login(username=credentials['username'], password=credentials['password'])

        self.client.get('/training')

        response = self.client.get(f'/learn_word/ru-en/{word.id}', follow=True)

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
        word = Word.objects.create(**smallpox, added_by=user)
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

        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials2['username'], password=credentials2['password'])

        response = self.client.get(f'/words/{word.id}/delete', follow=True)
        self.assertContains(response, status_code=200, text='something went wrong')
        self.assertEqual(Word.objects.all().count(), 1)

    def test_show_edit_page(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        pasha = User.objects.create_user(**credentials1)

        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials1['username'], password=credentials1['password'])

        response = self.client.get(f'/words/{word.id}/edit', follow=True)
        self.assertContains(response, status_code=200, text='smallpox')
        self.assertContains(response, status_code=200, text='оспа')
        self.assertContains(response, 'The children were all vaccinated against smallpox.')

    def test_update_word(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        data_to_update = {'word': 'smallpoxes', 'translation': 'натуральная оспа', 'sentence': 'cool smallpoxes'}

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        pasha = User.objects.create_user(**credentials1)

        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials1['username'], password=credentials1['password'])

        self.client.post(f'/words/{word.id}/edit/', data=data_to_update, follow=True)

        # self.assertContains(response, status_code=200, text=f'{data_to_update["word"]} was successfully updated!')
        word = Word.objects.last()
        self.assertEqual(word.sentence, 'cool smallpoxes')
        self.assertEqual(word.translation, 'натуральная оспа')

    def test_knowing_the_word(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        pasha = User.objects.create_user(**credentials1)
        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials1['username'], password=credentials1['password'])

        self.assertEqual(word.en_ru, False)

        self.assertEqual(word.ru_en, False)
        json_data = json.dumps({"id": word.id, "direction": "ru", "correctness": True})
        self.client.post(f'/learn_word/en-ru/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEqual(word.en_ru, True)
        self.assertEqual(word.ru_en, False)

    def test_unknowing_the_word(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
            'en_ru': True,
            'ru_en': True,
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        pasha = User.objects.create_user(**credentials1)
        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials1['username'], password=credentials1['password'])

        json_data = json.dumps({"id": word.id, "direction": "ru", "correctness": False})
        self.assertEqual(word.en_ru, True)
        self.assertEqual(word.ru_en, True)
        self.client.post(f'/learn_word/en-ru/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEqual(word.en_ru, False)
        self.assertEqual(word.ru_en, True)

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
        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials2['username'], password=credentials1['password'])

        self.assertEqual(word.en_ru, False)

        self.assertEqual(word.ru_en, False)
        json_data = json.dumps({"id": word.id, "direction": "ru", "correctness": True})
        self.client.post(f'/learn_word/en-ru/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEqual(word.en_ru, False)
        self.assertEqual(word.ru_en, False)

    def test_zero_count_of_words(self):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        pasha = User.objects.create_user(**credentials1)
        pasha = MyUser.objects.get(id=pasha.id)
        self.assertEqual(pasha.words().count(), 0)
        self.assertEqual(pasha.known_words().count(), 0)
        self.assertEqual(pasha.unknown_words().count(), 0)

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
        Word.objects.create(**smallpox, added_by=pasha)
        Word.objects.create(**canteen, added_by=pasha)
        Word.objects.create(**factory, added_by=pasha)

        pasha = MyUser.objects.get(id=pasha.id)
        self.assertEqual(pasha.words().count(), 3)
        self.assertEqual(pasha.known_words().count(), 0)
        self.assertEqual(pasha.unknown_words().count(), 3)

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
        pasha = User.objects.create_user(**credentials1)
        Word.objects.create(**smallpox, added_by=pasha, ru_en=True)
        Word.objects.create(**canteen, added_by=pasha, ru_en=True, en_ru=True)
        Word.objects.create(**factory, added_by=pasha, en_ru=True)

        pasha = MyUser.objects.get(id=pasha.id)
        self.assertEqual(pasha.words().count(), 3)
        self.assertEqual(pasha.known_words().count(), 1)
        self.assertEqual(pasha.unknown_words().count(), 2)


class ResetProgress(TestCase):
    def test_do_not_rest_progress(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
            'en_ru': True,
            'ru_en': True,
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com', }

        pasha = User.objects.create_user(**credentials1)

        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials1['username'], password=credentials1['password'])

        self.client.get(f'/words/{word.id}/reset/')

        word = Word.objects.get(id=word.id)
        self.assertFalse(word.ru_en)
        self.assertFalse(word.en_ru)


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

        for word in words:
            Word.objects.create(**word, added_by=pasha)

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

    def test_ru_en_direction(self):
        text, source_lang, target_lang = 'pen', 'en', 'ru'
        tt = TranslateText(source_lang, target_lang)

        result = tt.perform(text)
        self.assertEqual(result, 'ручка')

    def test_en_ru_direction(self):
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

        pasha = User.objects.create_user(**credentials1)
        vova = User.objects.create_user(**credentials2)

        User.objects.create_user(**credentials3)

        words = [
            {'word': 'smallpox',
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
            }, ]

        word4 = {
                    'word': 'cat',
                    'translation': 'кошка',
                    'sentence': 'it is very difficult to find black cat in black room.',
                }

        # create 3 words for Pasha
        for word in words:
            Word.objects.create(**word, added_by=pasha)

        # create 1 word for Vova
        Word.objects.create(**word4, added_by=vova)

    def test_retrieving_words_from_api_words(self):
        pasha = User.objects.get(username="pasha")
        auth_token = Token.objects.get(user_id=pasha.id).key

        response = self.client.get('/api/words/', headers={'Authorization': 'Token ' + auth_token})

        results = json.loads(response.content)

        self.assertEqual(results['count'], 3)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'][0]['word'], 'smallpox')
        self.assertEqual(results['results'][1]['word'], 'canteen')
        self.assertEqual(results['results'][2]['word'], 'factory')

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

    def test_words_from_api_when_user_has_not_any_words(self):
        dima = User.objects.get(username='dima')

        auth_token = Token.objects.get(user_id=dima.id).key

        response = self.client.get('/api/words/', headers={'Authorization': 'Token ' + auth_token})

        self.assertNotContains(response, text='Success', status_code=200)

        results = json.loads(response.content)

        self.assertEqual(results['count'], 0)
        self.assertEqual(results['next'], None)
        self.assertEqual(results['results'], [])
