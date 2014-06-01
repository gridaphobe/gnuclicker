from behave import *
from selenium.webdriver.support.ui import WebDriverWait


@when('we are logged in as {name}')
def step_impl(context, name):
    context.browser.get('http://gnuclicker.herokuapp.com/courses')
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_element_by_tag_name('button'))
    username = context.browser.find_element_by_id('universityId')
    username.send_keys(name)
    submit_btn = context.browser.find_element_by_tag_name('button')
    submit_btn.click()

b = {
    'Defense Against The Dark Arts': 'ab102e97-e312-49e1-a352-56237e834854',
    'CSE210': '0a61895b-41aa-445c-aa9c-5127cd0dad52',
    'RAINBOWS': '3b284a99-2d8f-4da6-a687-b17d3aa73afc'}

@when("we visit the course {course}")
def step_impl(context, course):
    course_btn = context.browser.find_element_by_link_text(course)
    course_btn.click()
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_elements_by_class_name('questions'))


@then("the course page for {course} is loaded")
def step_impl(context, course):
    assert context.browser.current_url == 'http://gnuclicker.herokuapp.com/courses/' + b[course] + '/questions' 

