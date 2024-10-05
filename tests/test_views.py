# from login.models import User
# from django.urls import reverse
# from django.test import Client, TestCase
# class TestViews(TestCase):
#     def setUp(self):
#         # self.client = Client()
#         self.user = User.objects.create(username='admin', password='admin')
#         self.login_url = reverse('login')
#     def test_login(self):
#         response = self.client.get(self.login_url)
#         self.assertEquals(response.status_code, 200)
#         self.assertTemplateUsed(response, 'login.html')
