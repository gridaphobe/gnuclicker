Feature: Login.

    Scenario: Login successfully.
      When we visit the login page
      And enter the username 'jstalin'
      And click submit
      Then the course page is loaded

    Scenario: Login unsuccessfully.
      When we visit the login page
      And enter the username 'jstalindd'
      And click submit
      Then the user receives an error



Feature: Navigating classes and questions.

    Scenario: Navigating classes.



    Scenario: Navigating questions.

