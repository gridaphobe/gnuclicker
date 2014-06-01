from behave import *
from selenium.webdriver.support.ui import WebDriverWait
import time

course_uuid = {
    'Defense Against The Dark Arts': 'ab102e97-e312-49e1-a352-56237e834854',
    'CSE210': '0a61895b-41aa-445c-aa9c-5127cd0dad52',
    'RAINBOWS': '3b284a99-2d8f-4da6-a687-b17d3aa73afc'}


lecture_uuid = {
    'NYAN': '80923fd6-a1c2-404f-9578-808894ec9dc0'
}


# ===============================================================
# GIVEN
# ===============================================================


@given('we are logged in as {name}')
def step_impl(context, name):
    context.browser.get('http://gnuclicker.herokuapp.com/courses')
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_element_by_tag_name('button'))
    username = context.browser.find_element_by_id('universityId')
    username.send_keys(name)
    submit_btn = context.browser.find_element_by_tag_name('button')
    submit_btn.click()


@given('we are on the course page')
def step_impl(context):
    context.browser.get('http://gnuclicker.herokuapp.com/courses')
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_elements_by_class_name('item'))


@given('we are viewing a question')
def step_impl(context):
    context.browser.get('http://gnuclicker.herokuapp.com/courses/0a61895b-41aa-445c-aa9c-5127cd0dad52/questions?questionId=df67b8fe-11f0-4def-82f7-941fabd3314a')
    wait_for_webpage_to_load(context)


# ===============================================================
# WHEN
# ===============================================================



@when("we visit the course {course}")
def step_impl(context, course):
    course_btn = context.browser.find_element_by_link_text(course)
    course_btn.click()
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_elements_by_class_name('questions'))



@when('we click on the first question of CSE210')
def step_impl(context):
    anchor_list = context.browser.find_elements_by_tag_name('a')
    for anchor in anchor_list:
        href = anchor.get_attribute('href')
        if 'questionId' in href:
            anchor.click()
            wait_for_webpage_to_load(context)
            return


@when('we select the {lecture_name} lesson')
def step_impl(context, lecture_name):
    anchor_list = context.browser.find_elements_by_tag_name('a')
    for anchor in anchor_list:
        if lecture_name in anchor.text:
            anchor.click()
            wait_for_webpage_to_load(context)
            return


@when('we click Home')
def step_impl(context):
    anchor_list = context.browser.find_elements_by_tag_name('a')
    for anchor in anchor_list:
        if anchor.text == 'Home':
            anchor.click()
            wait_for_webpage_to_load(context)
            return



# ===============================================================
# THEN
# ===============================================================

@then('we should be on the course page')
def step_impl(context):
    assert context.browser.current_url == 'http://gnuclicker.herokuapp.com/courses'


@then("the course page for {course} is loaded")
def step_impl(context, course):
    assert context.browser.current_url == 'http://gnuclicker.herokuapp.com/courses/' + course_uuid[course] + '/questions'


@then("the lecture page for {lecture} is loaded")
def step_impl(context, lecture):
    print ('lectureId=' + lecture_uuid[lecture])
    print context.browser.current_url
    assert ('lectureId=' + lecture_uuid[lecture]) in context.browser.current_url



@then('we should see the African option')
def step_impl(context):
    div_list = context.browser.find_elements_by_tag_name('div')
    for div in div_list:
        if div.text == 'African' and div.is_displayed():
            return
    assert False





# ===============================================================
# HELPER FUNCTIONS
# ===============================================================


def wait_for_webpage_to_load(context, timeout=20):
    start_time = time.time()
    while time.time() - start_time <= timeout:
        time.sleep(0.5)
        if 'complete' == context.browser.execute_script('return document.readyState'):
            return
    assert False # timeout

