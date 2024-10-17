# from django.test import TestCase
# from django.urls import reverse
# from django.core import mail
# from django.contrib.auth.models import User
# # from .models import User
# # Log In Tests
# class UserLogInTest(TestCase):
#     def setUp(self):
#         self.credentials = {
#             'username': 'testuser',
#             'password': 'secret'}
#         User.objects.create_user(**self.credentials)
#
#     def test_login(self):
#         # send login data
#         response = self.client.post('/login/', self.credentials, follow=True)
#         # should be logged in now
#         self.assertTrue(response.context['user'].is_active)
#     def test_login_incorrect_username(self):
#         response = self.client.post(reverse('login'), {
#             'username': 'invaliduser',
#             'password': 'validpassword',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'login.html')
#         self.assertContains(response, 'Invalid username or password.')
#
#     def test_login_incorrect_password(self):
#         response = self.client.post(reverse('login'), {
#             'username': 'validuser',
#             'password': 'invalidpassword',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'login.html')
#         self.assertContains(response, 'Invalid username or password.')
#
# # Sign Up Tests
# class UserSignUpTest(TestCase):
#     # ensure signup page is accessible
#     def setUp(self):
#         self.credentials = {
#             'username': 'testuser',
#             'password': 'secret'}
#         User.objects.create_user(**self.credentials)
#     def test_signup_view(self):
#         response = self.client.get(reverse('signup'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'signup.html')
#
#     # ensure signup when form is valid
#     def test_signup_valid_form(self):
#         response = self.client.get(reverse('signup'), {
#             'username': 'testnewusername',
#             'email': 'validemail@gmail.com',
#             'password1': 'val1dpassw0rd',
#             'password2': 'val1dpassw0rd'
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')
#         self.assertRedirects(response, reverse('login'))
#         self.assertTrue(User.objects.filter(username='validuser').exists())
#
#     # username already exists
#     def test_signup_existing_username(self):
#         response = self.client.post(reverse('signup'), {
#             'username': 'testuser',
#             'email': 'validemail@example.com',
#             'password1': 'val1dpassw0rd',
#             'password2': 'val1dpassw0rd',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'signup.html')
#         self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')
#
#     # password is too simple
#     def test_signup_simple_password(self):
#         response = self.client.post(reverse('signup'), {
#             'username': 'validuser',
#             'email': 'validemail@gmail.com',
#             'password1': '123456789',
#             'password2': '123456789',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'signup.html')
#         self.assertFormError(response, 'form', 'password2', 'This password is too common.')
#
#     # passwords do not match
#     def test_signup_mismatch_password(self):
#         response = self.client.post(reverse('signup'), {
#             'username': 'validuser',
#             'email': 'validemail@gmail.com',
#             'password1': 'pa55w0rd1',
#             'password2': 'pa55w0rd2',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertFormError(response, 'form', 'password2', 'The two password fields didn’t match.')
#
#
#
#
# # Forgot Password Tests
# class UserForgotPasswordTest(TestCase):
#     def setUp(self):
#         self.credentials = {
#             'username': 'testuser',
#             'password': 'secret'}
#         User.objects.create_user(**self.credentials)
#     def test_forgot_password_non_existent_email(self):
#         response = self.client.post(reverse('forgot_password'), {
#             'username':'testuser',
#             'email': 'nonexistent@example.com',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'forgot_password.html')
#         self.assertEqual(len(mail.outbox), 0)
#
#     def test_forgot_password_valid_email(self):
#         response = self.client.post(reverse('forgot_password'), {
#             'username':'testuser',
#             'email': 'x15968472900@163.com',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'forgot_password.html')
#         self.assertEqual(len(mail.outbox), 1)
#         self.assertIn('Password reset on', mail.outbox[0].subject)
#         self.assertIn(self.user.email, mail.outbox[0].to)