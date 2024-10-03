from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages import get_messages
import logging

logger = logging.getLogger(__name__)

class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_successful_login(self):
        with self.assertLogs('myapp', level='INFO') as cm:
            response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
            self.assertEqual(response.status_code, 302)  # Expecting a redirect
            self.assertRedirects(response, reverse('search_link'))  # Assuming 'search_link' is the redirect URL
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), 'You are now logged in.')
        self.assertEqual(cm.output, ['INFO:myapp:You are now logged in.'])

    def test_failed_login(self):
        with self.assertLogs('myapp', level='ERROR') as cm:
            response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpass'})
            self.assertEqual(response.status_code, 200)  # Expecting to stay on the login page
            self.assertIsInstance(response.context['form'], AuthenticationForm)
            self.assertFormError(response, 'form', None, 'Invalid username or password.')
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), 'Invalid username or password.')
        self.assertEqual(cm.output, ['ERROR:myapp:Invalid username or password.'])

    def test_get_request(self):
        with self.assertLogs('myapp', level='INFO') as cm:
            response = self.client.get(reverse('login'))
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.context['form'], AuthenticationForm)
        self.assertEqual(cm.output, ['INFO:myapp:GET request to login_user'])