from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User


# Sign Up Tests
class UserSignUpTest(TestCase):
    # ensure signup page is accessible
    def test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    # ensure signup when form is valid
    def test_signup_valid_form(self):
        response = self.client.get(reverse('signup'), {
            'username': 'validuser',
            'email': 'validemail@gmail.com',
            'password1': 'val1dpassw0rd',
            'password2': 'val1dpassw0rd'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='validuser').exists())

    # username already exists
    def test_signup_existing_username(self):
        response = self.client.post(reverse('signup'), {
            'username': 'admin',
            'email': 'validemail@example.com',
            'password1': 'val1dpassw0rd',
            'password2': 'val1dpassw0rd',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')

    # password is too simple
    def test_signup_simple_password(self):
        response = self.client.post(reverse('signup'), {
            'username': 'validuser',
            'email': 'validemail@gmail.com',
            'password1': '123456789',
            'password2': '123456789',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
        self.assertFormError(response, 'form', 'password2', 'This password is too common.')

    # passwords do not match
    def test_signup_mismatch_password(self):
        response = self.client.post(reverse('signup'), {
            'username': 'validuser',
            'email': 'validemail@gmail.com',
            'password1': 'pa55w0rd1',
            'password2': 'pa55w0rd2',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', 'The two password fields didn’t match.')


# Log In Tests
class UserLogInTest(TestCase):
    def test_valid_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'validuser',
            'password': 'validpassword',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('search'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_incorrect_username(self):
        response = self.client.post(reverse('login'), {
            'username': 'invaliduser',
            'password': 'validpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Invalid username or password.')

    def test_login_incorrect_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'validuser',
            'password': 'invalidpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Invalid username or password.')


# Forgot Password Tests
class UserForgotPasswordTest(TestCase):
    def test_forgot_password_non_existent_email(self):
        response = self.client.post(reverse('forgot_password'), {
            'email': 'nonexistent@example.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertEqual(len(mail.outbox), 0)

    def test_forgot_password_valid_email(self):
        response = self.client.post(reverse('forgot_password'), {
            'email': 'validemail@gmail.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forgot_password.html')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password reset on', mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)