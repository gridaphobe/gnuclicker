Feature: Go to each course.

  Scenario: Go to a course.
    Given we are logged in as jstalin
    When we visit the course CSE210
    Then the course page for CSE210 is loaded
  


  Scenario: Go to a question from the main course page.
    Given we are logged in as jstalin
    And we are on the course page
    When we visit the course CSE210
    And we click on the first question of CSE210
    Then we should see the African option


  Scenario: Go to a the Nyan lesson.
    Given we are logged in as jbox
    And we are on the course page
    When we visit the course RAINBOWS
    And we select the NYAN lesson
    Then the lecture page for NYAN is loaded


  Scenario: Return to course page.
    Given we are logged in as jstalin
    And we are on the course page
    When we visit the course CSE210
    And we click on the first question of CSE210
    And we click Home
    Then we should be on the course page
