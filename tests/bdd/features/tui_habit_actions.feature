# language: en
Feature: TUI Habit Instance Actions (BR-TUI-010)
  As a TimeBlock user
  I want to mark habit instances as done or skip in the TUI
  So that I can track my daily execution

  # R01: Lista instâncias do dia
  Scenario: Shows today's instances grouped by habit
    Given the HabitsScreen is active
    And there are instances for today
    Then instances should be listed grouped by habit name
    And each instance should show scheduled time and status

  # R02: Menu de ação em instância pendente
  Scenario: Enter on pending instance opens action menu
    Given the HabitsScreen is active
    And a pending instance is selected
    When the user presses 'enter'
    Then an action menu should appear with Done and Skip options

  Scenario: Enter on completed instance is readonly
    Given the HabitsScreen is active
    And a completed instance is selected
    When the user presses 'enter'
    Then no action menu should appear

  # R03: Done solicita duração
  Scenario: Mark done asks for actual duration
    Given the action menu is open
    When the user selects Done
    Then a duration input should appear
    And the substatus should be calculated from duration

  # R04: Skip solicita categoria
  Scenario: Mark skip asks for reason category
    Given the action menu is open
    When the user selects Skip
    Then a category selection should appear with all SkipReason options

  Scenario: Skip with optional note
    Given the skip reason is selected
    Then an optional note input should appear

  # R05: Status com cor
  Scenario: Done instance shows green indicator
    Given an instance has status DONE
    Then it should display with success color and checkmark

  Scenario: Skipped instance shows yellow indicator
    Given an instance has status NOT_DONE with substatus SKIPPED
    Then it should display with warning color and cross mark

  Scenario: Pending instance shows neutral indicator
    Given an instance has status PENDING
    Then it should display with muted color and dot indicator
