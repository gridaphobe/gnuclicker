from behave import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import time
import utilities
# course_uuid = {
#     'Defense Against The Dark Arts': 'ab102e97-e312-49e1-a352-56237e834854',
#     'CSE210': '0a61895b-41aa-445c-aa9c-5127cd0dad52',
#     'RAINBOWS': '3b284a99-2d8f-4da6-a687-b17d3aa73afc'}
#
#
# lecture_uuid = {
#     'NYAN': '80923fd6-a1c2-404f-9578-808894ec9dc0'
# }


# ===============================================================
# GIVEN
# ===============================================================


@given('we are logged in as {name}')
def step_impl(context, name):
    context.browser.get('http://' + utilities.HOSTNAME + '/courses')
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_element_by_tag_name('button'))
    username = context.browser.find_element_by_id('universityId')
    username.send_keys(name)
    submit_btn = context.browser.find_element_by_tag_name('button')
    submit_btn.click()


@given('we are on the course page')
def step_impl(context):
    context.browser.get('http://' + utilities.HOSTNAME + '/courses')
    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_elements_by_class_name('item'))



# ===============================================================
# WHEN
# ===============================================================

@when("we click the add question button")
def step_impl(context):
    add_link = context.browser.find_element_by_xpath("//div[@class='questions']/a[@class='item add']")
    add_link.click()
    utilities.wait_for_webpage_to_load(context)


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
            utilities.wait_for_webpage_to_load(context)
            return


@when('we select the {lecture_name} lesson')
def step_impl(context, lecture_name):
    anchor_list = context.browser.find_elements_by_tag_name('a')
    for anchor in anchor_list:
        if lecture_name in anchor.text:
            anchor.click()
            utilities.wait_for_webpage_to_load(context)
            return


@when('we click Home')
def step_impl(context):
    anchor_list = context.browser.find_elements_by_tag_name('a')
    for anchor in anchor_list:
        if anchor.text == 'Home':
            anchor.click()
            utilities.wait_for_webpage_to_load(context)
            return

title = "this was created by selenium"
edited_title = "this was edited by selenium!"

@when("we edit the '{question_name}' question")
def step_impl(context, question_name):
# currently ignores the question_name param since that would require resetting the db between each run
    question = context.browser.find_element_by_link_text(title)
    question.click()

    context.browser.implicitly_wait(5)
    edit_btn = context.browser.find_element_by_link_text('Edit Question')
    edit_btn.click()

    utilities.wait_for_webpage_to_load(context)

    title_field = context.browser.find_element_by_id('title')
    title_field.clear()
    title_field.send_keys(edited_title)

    for x in range(0, 5):
        choice_field = context.browser.find_element_by_id('choices-' + str(x) + '-answer')
        choice_field.clear()
        choice_field.send_keys('EDIT: Nobody believes choice ' + str(x))
    
    title_field.submit()
    utilities.wait_for_webpage_to_load(context)

@when('we add a new question')
def step_impl(context):
    prompt = "Which choice do you believe?"
    
    title_field = context.browser.find_element_by_id('title')
    prompt_field = context.browser.find_element_by_id('prompt')
    choice_3_correct = context.browser.find_element_by_id('choices-3-correct')

    title_field.send_keys(title)
    prompt_field.send_keys(prompt)

    for x in range(0, 5):
        choice_field = context.browser.find_element_by_id('choices-' + str(x) + '-answer')
        choice_field.send_keys('I believe choice ' + str(x))

    choice_3_correct.click()
    title_field.submit()
    utilities.wait_for_webpage_to_load(context)


# ===============================================================
# THEN
# ===============================================================

@then('our question has been edited')
def step_impl(context):
    question = context.browser.find_element_by_link_text(edited_title)
    question.click()
    
    div_list = context.browser.find_elements_by_css_selector('div.text')

    found_choices = 0

    for div in div_list:
        if 'EDIT: Nobody believes choice ' in div.text and div.is_displayed():
            found_choices += 1
    assert found_choices == 5

@then('our question has been added')
def step_impl(context):
    question = context.browser.find_element_by_link_text(title)
    question.click()
    
    div_list = context.browser.find_elements_by_css_selector('div.text')

    found_choices = 0

    for div in div_list:
        if 'I believe choice ' in div.text and div.is_displayed():
            found_choices += 1
    assert found_choices == 5

@then('we should be on the course page')
def step_impl(context):
    assert context.browser.current_url == 'http://' + utilities.HOSTNAME + '/courses'



@then("the course page for {course} is loaded")
def step_impl(context, course):

    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_element_by_class_name('heading'))

    # We should see the course name as the title of the dropdown list.
    for a_tag in context.browser.find_elements_by_tag_name('a'):
        if course in a_tag.text and a_tag.get_attribute('href').endswith('#'):
            return # Good

    assert False # Badness



@then("the lecture page for {lecture} is loaded")
def step_impl(context, lecture):

    WebDriverWait(context.browser, 30).until(lambda driver: driver.find_element_by_class_name('lessons'))

    # We should see the lecture name highlighted in purple.
    for highlighted_a_tag in context.browser.find_elements_by_xpath("//div[@class='item sel']/a"):
        if highlighted_a_tag.text == lecture:
            return

    assert False


@then('we should see the African option')
def step_impl(context):
    div_list = context.browser.find_elements_by_tag_name('div')
    for div in div_list:
        if div.text == 'African' and div.is_displayed():
            return
    assert False






