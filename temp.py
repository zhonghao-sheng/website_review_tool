# -*- coding: utf-8 -*-
# @Time    : 2024/5/7 21:16
# @Author  : 顾安
# @File    : 7.动作链.py
# @Software: PyCharm
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

browser = webdriver.Chrome()
browser.get('http://www.runoob.com/try/try.php?filename=jqueryui-api-droppable')

iframe = browser.find_element(By.XPATH, '//iframe[@id="iframeResult"]')
browser.switch_to.frame(iframe)

source = browser.find_element(By.ID, 'draggable')
target = browser.find_element(By.ID, 'droppable')

# 创建动作链对象
actions = ActionChains(browser)
actions.drag_and_drop(source, target)
actions.perform()  # 动作激活

time.sleep(3)
browser.quit()
