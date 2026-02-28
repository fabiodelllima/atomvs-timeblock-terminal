# language: en
Feature: TUI CRUD Operations Pattern (BR-TUI-005)
  As a TimeBlock user
  I want consistent CRUD interactions across all screens
  So that I can manage items predictably

  # R01: Keybindings consistentes
  Scenario: Create with 'n' or 'a' keybinding
    Given a CRUD screen is active
    When the user presses 'n'
    Then a create form should appear

  Scenario: Edit with 'e' keybinding
    Given a CRUD screen is active
    And an item is selected
    When the user presses 'e'
    Then an edit form should appear with prefilled data

  Scenario: Delete with 'x' keybinding
    Given a CRUD screen is active
    And an item is selected
    When the user presses 'x'
    Then a delete confirmation should appear

  Scenario: View details with 'enter' keybinding
    Given a CRUD screen is active
    And an item is selected
    When the user presses 'enter'
    Then item details should be displayed

  # R05: Confirmação de delete
  Scenario: Delete confirmation shows item name
    Given a CRUD screen is active
    And an item "Academia" is selected
    When the user presses 'x'
    Then the confirmation should contain "Academia"
    And the confirmation should require 'y' to proceed

  # R06: Session per action
  Scenario: Each operation uses independent session
    Given a CRUD screen is active
    When the user creates an item
    Then a new database session should be used
    And the session should be closed after the operation

  # R07: Auto-refresh após operação
  Scenario: List refreshes after successful create
    Given a CRUD screen is active
    When the user creates an item successfully
    Then the item list should refresh automatically

  # R08: Erros inline
  Scenario: Validation errors shown inline
    Given a create form is open
    When the user submits with invalid data
    Then the error should be shown inline in the form
    And no modal should appear
