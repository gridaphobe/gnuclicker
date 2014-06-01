Feature: Login.

    Scenario: Login successfully.
      When we visit the login page
      And enter the username 'jstalin'
      And click submit
      Then the course page is loaded

    Scenario: Login with invalid username.
      When we visit the login page
      And enter the username 'jstalindd'
      And click submit
      Then the user receives an error



Feature: Navigating classes and questions.

    Scenario: Navigating classes.



    Scenario: Navigating questions.
