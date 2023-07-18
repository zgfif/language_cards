import datetime

from django.contrib.auth.models import User
from django.test import TestCase


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
        response = self.client.get('/add_word')
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
        failure_message = f'You have not entered any word!'
        self.assertContains(response, text=failure_message, status_code=200)
