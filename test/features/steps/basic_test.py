from behave import *
from selenium.webdriver.support.ui import WebDriverWait
import utilities


@when('we visit the login page')
def step_impl(context):
    context.browser.get('http://' + utilities.HOSTNAME + '/courses')
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_element_by_tag_name('button'))



@when("enter the username '{name}'")
def step_impl(context, name):
    username = context.browser.find_element_by_id('universityId')
    username.send_keys(name)



@when('click submit')
def step_impl(context):
    submit_btn = context.browser.find_element_by_tag_name('button')
    submit_btn.click()



@then('the course page is loaded')
def step_impl(context):
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_element_by_class_name('heading'))
    print context.browser.current_url
    assert context.browser.current_url == 'http://' + utilities.HOSTNAME + '/courses'



@then('the user receives an error')
def step_impl(context):
    assert context.browser.current_url == 'http://' + utilities.HOSTNAME + '/login'
