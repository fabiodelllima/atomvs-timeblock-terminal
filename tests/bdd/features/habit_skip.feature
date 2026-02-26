# language: en
# BR-HABIT-SKIP-001: Skip de hábito com categorização
Feature: Habit Skip with Categorization (BR-HABIT-SKIP-001)
  As a TimeBlock user
  I want to mark habits as skipped with a category
  So that I can track interruption reasons and identify patterns

  Background:
    Given a routine "Rotina Matinal" exists
    And a habit "Academia" is scheduled for today at 07:00-08:30
    And a HabitInstance with status "PENDING" exists

  # Cenário 1: Skip com categoria HEALTH e nota
  Scenario: Skip with category HEALTH
    When the user marks skip with category "HEALTH" and note "Gripe, febre 38°C"
    Then the status should be "NOT_DONE"
    And the substatus should be "SKIPPED_JUSTIFIED"
    And the skip_reason should be "saude"
    And the skip_note should be "Gripe, febre 38°C"
    And done_substatus should be NULL
    And completion_percentage should be NULL

  # Cenário 2: Skip com categoria WORK sem nota
  Scenario: Skip with category WORK without note
    When the user marks skip with category "WORK" without note
    Then the status should be "NOT_DONE"
    And the substatus should be "SKIPPED_JUSTIFIED"
    And the skip_reason should be "trabalho"
    And the skip_note should be NULL

  # Cenário 7: Erro - instância inexistente
  Scenario: Error when skipping nonexistent instance
    When the user tries to skip HabitInstance with ID 99999
    Then the system should return error "HabitInstance 99999 not found"

  # Cenário 8: Erro - nota muito longa (>500 chars)
  Scenario: Error when skip note is too long
    Given the skip_note has 501 characters
    When the user tries skip with category "HEALTH" and that note
    Then the system should return error "Skip note must be <= 500 characters"
