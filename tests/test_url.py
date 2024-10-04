from django.test import TestCase, Client, SimpleTestCase
from django.urls import reverse, resolve
from login.views import login_user, signup, index
from search_link.views import search_link
class TestUrls(SimpleTestCase):
    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login_user)

    def test_search_url_resolves(self):
        url = reverse('search_link')
        self.assertEquals(resolve(url).func, search_link)

    def test_signup_url_resolves(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func, signup)

    def test_index_url_resolves(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, index)