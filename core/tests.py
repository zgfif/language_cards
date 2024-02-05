import datetime
import json

from django.contrib import auth
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from core.lib.word_ids import WordIds
from core.models import Word, MyUser


class IndexViewTests(TestCase):
    def test_have_recent_words(self):
        response = self.client.get('/')
        text = 'Sign in'
        self.assertContains(response, text=text, status_code=200)


class SignUpViewTests(TestCase):
    def test_have_form_to_signup(self):
        response = self.client.get('/signup')
        text = 'Password confirmation'
        self.assertContains(response, text=text, status_code=200)

    def test_successful_registration(self):
        user_data = {'username': 'pasha',
                'email': 'zihzag@gmail.com',
                'password': '12345678',
                'password_confirmation': '12345678',
        }

        response = self.client.post('/signup', user_data, follow=True)
        text = 'Congratulations! You have successfully registered!'
        self.assertContains(response, text=text, status_code=200)

    def test_if_username_is_busy(self):
        user_data = {'username': 'pasha',
                     'email': 'zihzag@gmail.com',
                     'password': '12345678',
                     }

        User.objects.create_user(**user_data)
        response = self.client.post('/signup', {'username': 'pasha', 'email': 'pasha@gmail.com', 'password': '1234', 'password_confirmation': '1234'})
        text = 'Entered username or/and email is already exists'
        self.assertContains(response, text=text, status_code=200)

    def test_if_email_is_busy(self):
        user_data = {'username': 'pasha',
                     'email': 'zihzag@gmail.com',
                     'password': '12345678',
                     }

        User.objects.create_user(**user_data)
        response = self.client.post('/signup', {'username': 'Pavel', 'email': 'zihzag@gmail.com', 'password': '1234', 'password_confirmation': '1234'})
        text = 'Entered username or/and email is already exists'
        self.assertContains(response, text=text, status_code=200)

    def test_if_password_and_password_confirmation_different(self):
        response = self.client.post('/signup', {'username': 'Pavel', 'email': 'zihzag@gmail.com', 'password': '1234', 'password_confirmation': '12345'})
        text = 'Password and Password confirmation must be the same'
        self.assertContains(response, text=text, status_code=200)


class SignInViewTests(TestCase):
    def test_has_form_to_signin(self):
        response = self.client.get('/signin')
        self.assertContains(response, text='password', status_code=200)
        self.assertContains(response, text='username/email', status_code=200)

    def test_incorrect_username(self):
        User.objects.create_user(username='Pavel', password='1asdfX')
        response = self.client.post('/signin', {'username': 'pasha', 'password': '1asdfX'})
        self.assertContains(response, text='Incorrect username/email/password', status_code=200)
        self.assertNotContains(response, text='Sign out', status_code=200)

    def test_incorrect_email(self):
        User.objects.create_user(username='pasha', password='1asdfX', email='zihzag@gmail.com')
        response = self.client.post('/signin', {'username': 'pasha@gmail.com', 'password': '1asdfX'})
        self.assertContains(response, text='Incorrect username/email/password', status_code=200)
        self.assertNotContains(response, text='Sign out', status_code=200)

    def test_incorrect_password(self):
        User.objects.create_user(username='pasha', password='1asdfX', email='zihzag@gmail.com')
        response = self.client.post('/signin', {'username': 'zihzag@gmail.com', 'password': '111111'})
        self.assertContains(response, text='Incorrect username/email/password', status_code=200)
        self.assertNotContains(response, text='Sign out', status_code=200)

    def test_by_email(self):
        User.objects.create_user(username='pasha', password='1asdfX', email='zihzag@gmail.com')
        response = self.client.post('/signin', {'username': 'zihzag@gmail.com', 'password': '1asdfX'}, follow=True)
        self.assertContains(response, text='Hello', status_code=200)
        self.assertContains(response, text='Sign out', status_code=200)

    def test_by_username(self):
        User.objects.create_user(username='pasha', password='1asdfX', email='zihzag@gmail.com')
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
    def test_opening_profile_without_authorization(self):
        User.objects.create_user(username='pasha', password='1asdfX')
        response = self.client.get('/profile', follow=True)
        self.assertContains(response, text='username/email', status_code=200)
        self.assertContains(response, text='password')

    def test_access_to_account_with_authorization(self):
        User.objects.create_user(username='pasha', password='1asdfX', email='pasha@gmail.com')
        self.client.login(username='pasha', password='1asdfX')
        response = self.client.get('/profile')
        self.assertContains(response, text='pasha', status_code=200)
        self.assertContains(response, text='pasha@gmail.com', status_code=200)
        self.assertContains(response, text=datetime.date.today())


class AddWordViewTests(TestCase):
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
        self.assertEquals(Word.objects.filter(word=word_details['word']).count(), 1)
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
        self.assertEquals(Word.objects.filter(word=word_details['word']).count(), 1)
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
        self.assertContains(response, text='you have not any words yet:)', status_code=200)

    def test_absense_of_words_related_to_other_user(self):
        user1 = User.objects.create_user(username='pasha', password='1asdfX', email='pasha@gmail.com')
        user2 = User.objects.create_user(username='vadim', password='G?1wraas4', email='vadim@gmail.com')

        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        flu = {
            'word': 'flu',
            'translation': 'грипп',
            'sentence': 'I had a bad case of the flu.',
        }

        fever = {
            'word': 'fever',
            'translation': 'лихорадка',
            'sentence': 'I would take aspirin to help me with the pain and reduce the fever',
        }

        Word.objects.create(added_by=user1, **smallpox)
        Word.objects.create(added_by=user1, **flu)
        Word.objects.create(added_by=user2, **fever)

        self.client.login(username='pasha', password='1asdfX')
        response = self.client.get('/words')
        self.assertContains(response, status_code=200, text='smallpox')
        self.assertContains(response, status_code=200, text='flu')
        self.assertNotContains(response, status_code=200, text='fever')


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
        self.assertContains(response, status_code=200, text="You haven't word yet :(")
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
        self.assertEquals(Word.objects.filter(added_by=user).count(), 1)

        self.client.get(f'/words/{word.id}/delete/')

        self.assertEquals(Word.objects.filter(added_by=user).count(), 0)

    def test_drop_unexisting_id_word(self):
        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        user = User.objects.create_user(**credentials)

        self.client.login(username=credentials['username'], password=credentials['password'])

        credentials = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        self.client.login(username=credentials['username'], password=credentials['password'])

        response = self.client.get('/words/unexisting_id/delete')
        self.assertEquals(response.status_code, 404)

    def test_trying_to_remove_not_your_word(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        credentials2 = {'username': 'alex', "password": '24safkl', 'email': 'alex@gmail.com'}

        pasha = User.objects.create_user(**credentials1)
        alex = User.objects.create_user(**credentials2)

        self.assertEquals(User.objects.all().count(), 2)

        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials2['username'], password=credentials2['password'])

        response = self.client.get(f'/words/{word.id}/delete', follow=True)
        self.assertContains(response, status_code=200, text='something went wrong')
        self.assertEquals(Word.objects.all().count(), 1)

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

        response = self.client.post(f'/words/{word.id}/edit/', data=data_to_update, follow=True)

        self.assertContains(response, status_code=200, text='натуральная оспа')
        self.assertContains(response, status_code=200, text=f'{data_to_update["word"]} was successfully updated!')
        self.assertEqual(Word.objects.last().sentence, 'cool smallpoxes')


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

        self.assertEquals(word.en_ru, False)

        self.assertEquals(word.ru_en, False)
        json_data = json.dumps({"id": word.id, "direction": "ru", "correctness": True})
        self.client.post(f'/learn_word/en-ru/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEquals(word.en_ru, True)
        self.assertEquals(word.ru_en, False)

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
        self.assertEquals(word.en_ru, True)
        self.assertEquals(word.ru_en, True)
        self.client.post(f'/learn_word/en-ru/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEquals(word.en_ru, False)
        self.assertEquals(word.ru_en, True)

    def test_change_knowing_the_word_by_another_user(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}
        credentials2 = {'username': 'dima', "password": '1akklk', 'email': 'dima@gmail.com'}
        pasha = User.objects.create_user(**credentials1)
        dima = User.objects.create_user(**credentials2)
        word = Word.objects.create(**smallpox, added_by=pasha)

        self.client.login(username=credentials2['username'], password=credentials1['password'])

        self.assertEquals(word.en_ru, False)

        self.assertEquals(word.ru_en, False)
        json_data = json.dumps({"id": word.id, "direction": "ru", "correctness": True})
        self.client.post(f'/learn_word/en-ru/{word.id}/', data=json_data, content_type='application/json')
        word = Word.objects.last()
        self.assertEquals(word.en_ru, False)
        self.assertEquals(word.ru_en, False)

    def test_zero_count_of_words(self):
        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com'}

        pasha = User.objects.create_user(**credentials1)
        pasha = MyUser.objects.get(id=pasha.id)
        self.assertEquals(pasha.words().count(), 0)
        self.assertEquals(pasha.known_words().count(), 0)
        self.assertEquals(pasha.unknown_words().count(), 0)


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
        self.assertEquals(pasha.words().count(), 3)
        self.assertEquals(pasha.known_words().count(), 0)
        self.assertEquals(pasha.unknown_words().count(), 3)

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
        self.assertEquals(pasha.words().count(), 3)
        self.assertEquals(pasha.known_words().count(), 1)
        self.assertEquals(pasha.unknown_words().count(), 2)


class ResetProgress(TestCase):
    def test_do_not_rest_progress(self):
        smallpox = {
            'word': 'smallpox',
            'translation': 'оспа',
            'sentence': 'The children were all vaccinated against smallpox.',
            'en_ru': True,
            'ru_en': True,
        }

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com',}

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
        },]

        credentials1 = {'username': 'pasha', "password": '1asdfX', 'email': 'pasha@gmail.com',}

        pasha = User.objects.create_user(**credentials1)

        for word in words:
            Word.objects.create(**word, added_by=pasha)

        self.client.login(**credentials1)

        self.assertEqual(self.client.session.get('word_ids', None), None)

        words_objects = Word.objects.all()
        self.client.get('/')
        session_ids = [word.id for word in words_objects]
        self.assertEqual(len(session_ids), 3)
