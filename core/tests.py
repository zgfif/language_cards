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
