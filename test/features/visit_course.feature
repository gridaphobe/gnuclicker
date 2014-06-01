Feature: Go to each course.

  Scenario: Go to a course.
    When we are logged in as jstalin
    And we visit the course RAINBOWS 
    Then the course page for RAINBOWS is loaded
  
