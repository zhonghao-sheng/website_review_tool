from django.test import TestCase, Client
from django.urls import reverse
from login.models import User


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='admin', password='admin')
        self.login_url = reverse('login')  # Ensure 'login' is the correct name for your login URL

    def test_login(self):
        # Simulate a POST request to the login view with the correct credentials
        response = self.client.post(self.login_url, {'username': 'admin', 'password': 'admin'})

        # Check that the response status code is 302 (redirect after successful login)
        self.assertEqual(response.status_code, 302)

        # Optionally, check that the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)