# language: en
Feature: TUI Screen Navigation (BR-TUI-002)
  As a TimeBlock TUI user
  I want to navigate between screens using keyboard shortcuts
  So that I can access different features without typing commands

  # BR-TUI-002: Navegação entre screens (refinamento - troca real de conteúdo)

  Scenario: Dashboard is the initial screen
    Given the TUI is open
    Then the active screen is "dashboard"
    And the content area shows the Dashboard

  Scenario: Navigating to Routines swaps content
    Given the TUI is open
    When I press "2"
    Then the active screen is "routines"
    And the content area shows the Routines screen
    And the Dashboard is not visible

  Scenario: Navigating to Habits swaps content
    Given the TUI is open
    When I press "3"
    Then the active screen is "habits"
    And the content area shows the Habits screen

  Scenario: Navigating to Tasks swaps content
    Given the TUI is open
    When I press "4"
    Then the active screen is "tasks"
    And the content area shows the Tasks screen

  Scenario: Navigating to Timer swaps content
    Given the TUI is open
    When I press "5"
    Then the active screen is "timer"
    And the content area shows the Timer screen

  Scenario: NavBar reflects active screen
    Given the TUI is open
    When I press "r"
    Then the NavBar indicates "routines" as active

  Scenario: Escape returns to Dashboard with content swap
    Given the TUI is open
    And I am on the "routines" screen
    When I press "escape"
    Then the active screen is "dashboard"
    And the content area shows the Dashboard

  Scenario: Sequential navigation swaps content correctly
    Given the TUI is open
    When I press "2"
    Then the content area shows the Routines screen
    When I press "3"
    Then the content area shows the Habits screen
    When I press "1"
    Then the content area shows the Dashboard
