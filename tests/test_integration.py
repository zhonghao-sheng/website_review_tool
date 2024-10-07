from selenium import webdriver
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from selenium.webdriver.common.by import By
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestLoginPage(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)
    def tearDown(self):
        self.browser.quit()

    def test_login_page(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.XPATH, '/html/body/p/a[1]').click()
        login_url = self.live_server_url + reverse('login')
        time.sleep(1)
        self.assertEqual(login_url, self.browser.current_url)

    def test_search(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.XPATH, '/html/body/p/a[1]').click()
        self.browser.find_element(By.ID, 'username').send_keys('testuser')
        self.browser.find_element(By.ID, 'password').send_keys('secret')
        self.browser.find_element(By.XPATH, "//button[text()='LOGIN']").click()
        try:
            WebDriverWait(self.browser, 2).until(EC.url_changes(self.live_server_url + reverse('login')))
        except Exception as e:
            self.fail(f"Login failed: {e}")

            # Check if the login was successful by checking the URL
        current_url = self.browser.current_url
        expected_url = self.live_server_url + reverse('search_link')  # Replace with your expected URL after login
        time.sleep(10)
        self.assertEqual(current_url, expected_url, "Login failed: URL did not match expected URL")
    def test_search_page_redirect(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.XPATH, '/html/body/p/a[1]').click()
        self.browser.find_element(By.ID, 'username').send_keys('testuser')
        self.browser.find_element(By.ID, 'password').send_keys('secret')
        self.browser.find_element(By.XPATH, "//button[text()='LOGIN']").click()
        try:
            WebDriverWait(self.browser, 2).until(EC.url_changes(self.live_server_url + reverse('login')))
        except Exception as e:
            self.fail(f"Login failed: {e}")

            # Check if the login was successful by checking the URL
        current_url = self.browser.current_url
        expected_url = self.live_server_url + reverse('search_link')  # Replace with your expected URL after login
        self.assertEqual(current_url, expected_url, "Login failed: URL did not match expected URL")

    def test_search_result_redirect(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.XPATH, '/html/body/p/a[1]').click()
        self.browser.find_element(By.ID, 'username').send_keys('testuser')
        self.browser.find_element(By.ID, 'password').send_keys('secret')
        self.browser.find_element(By.XPATH, "//button[text()='LOGIN']").click()
        try:
            WebDriverWait(self.browser, 2).until(EC.url_changes(self.live_server_url + reverse('login')))
        except Exception as e:
            self.fail(f"Login failed: {e}")

            # Check if the login was successful by checking the URL
        current_url = self.browser.current_url
        expected_url = self.live_server_url + reverse('search_link')  # Replace with your expected URL after login
        self.assertEqual(current_url, expected_url, "Login failed: URL did not match expected URL")
        self.browser.find_element(By.ID, 'url').send_keys('invalid link')
        self.browser.find_element(By.ID, 'searchLinks').click()
        time.sleep(2)
        current_url = self.browser.current_url
        expected_url = self.live_server_url + reverse('show_results')
        self.assertEqual(current_url, expected_url, "Login failed: URL did not match expected URL")

