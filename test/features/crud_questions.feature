Feature: Create, add, edit, delete questions as an instructor.

  Scenario: Add a new question.
    Given we are logged in as jbox
    And we are on the course page
    When we visit the course RAINBOWS
    And we select the NYAN lesson
    And we click the add question button
    And we add a new question
    Then our question has been added
  
  Scenario: Edit a question.
    Given we are logged in as jbox
    And we are on the course page
    When we visit the course RAINBOWS
    And we select the NYAN lesson
    And we edit the 'WTF MATE?' question
    Then our question has been edited
