# @File    : 3.登录网易邮箱.py
# @Software: PyCharm


import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class LoginEmail:
    def __init__(self):
        self.browser = webdriver.Chrome()


    def open_email(self, url):
        self.browser.get(url)
        time.sleep(1)

    def login(self, address, password, SMScode):

        self.browser.find_element(By.XPATH, '/html/body/div[3]/main/div[2]/div/div/div[2]/form/div[1]/div[3]/div/div[2]/span/input').send_keys(address)
        time.sleep(1)
        self.browser.find_element(By.XPATH, '/html/body/div[3]/main/div[2]/div/div/div[2]/form/div[2]/input').click()
        time.sleep(1)
        self.browser.find_element(By.XPATH, '/html/body/div[3]/main/div[2]/div/div/div[2]/form/div[1]/div[4]/div/div[2]/span/input').send_keys(password)
        time.sleep(1)
        self.browser.find_element(By.XPATH,
                                  '/html/body/div[3]/main/div[2]/div/div/div[2]/form/div[2]/input').click()
        time.sleep(1)
        self.browser.find_element(By.XPATH,'//*[@id="form70"]/div[2]/div/div[1]/div[2]/div[2]/a').click()
        time.sleep(1)

        self.browser.find_element(By.XPATH, '/html/body/div[3]/main/div[2]/div/div/div[2]/form/div[1]/div[4]/div/div[2]/span/input').send_keys(SMScode)
        time.sleep(1000)
        self.browser.find_element(By.XPATH, '/html/body/div[3]/main/div[2]/div/div/div[2]/form/div[2]/input').click()
        time.sleep(1000)

    def close_browser(self):
        self.browser.quit()


if __name__ == '__main__':
    login_email = LoginEmail()
    login_email.open_email('https://sso.unimelb.edu.au/app/universityofmelbourne_studentportal_1/exk7v59xzIPDUTnNC3l6/sso/saml?SAMLRequest=fVLvT8IwEP1Xln7f2g1UaGDJhBhIAAkMJX4hZSuyuLWzdyXoX2%2BHP4gm8vFe37u79649BYwnFvdqIV%2BtBPSOVamAO7hPrFFcCyhcKSoJHDO%2BTKYTHgWM10ajznRJfgThZYEAkAYLrYg3HvZJkfsZlunjbN2KRh3ZSdZ6SrwHacBR%2BsQpHA%2FAyrECFAodxKK2z7o%2Bi9Iw5KzNGXsi3tDtXCiBJ9UesQZOKYAOrCoqWW4DmdtAWCrqmjro0AzAN71r3rTbV24AbS4V1tqgKDchlceXm8NV9%2Fg%2Bng9XqZoNWuV105GCqJzd%2BZfx20LlhXq%2BbHr7SQI%2BStO5P79fpsRLvoMYaAW2kmYpzaHI5GoxOTuo3v4aaKZHG%2BFORUUGlMQ9Fzk%2FRWS8O20qgZd3aRCX%2Bu5E5c6xy4HE%2Fw7s0XP%2FuCl%2B%2F5P4Aw%3D%3D')

