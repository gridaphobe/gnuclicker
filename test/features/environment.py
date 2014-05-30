from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import os
import subprocess


def before_all(context):
    subprocess.call('killall -9 firefox', shell=True)
    os.environ['DISPLAY'] = ':0.0'
    context.browser = webdriver.Firefox()


def before_scenario(context, scenario):
    context.browser.get('http://gnuclicker.herokuapp.com/logout')
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_element_by_tag_name('button'))


def after_all(context):
    context.browser.quit()
