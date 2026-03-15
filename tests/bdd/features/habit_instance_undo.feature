# language: en
# BR-HABITINSTANCE-007: Undo with TimeLog preservation
Feature: Habit Instance Undo (BR-HABITINSTANCE-007)
  As a TimeBlock user
  I want to undo a habit's completion or skip
  So that I can correct accidental status changes while preserving time tracking records

  Background:
    Given a routine "Rotina Matinal" exists
    And a habit "Exercício" is scheduled for today at 08:00-09:00
    And a HabitInstance with status "PENDING" exists

  # Cenário 1: Undo de hábito marcado como DONE
  Scenario: Undo from DONE clears all completion fields
    Given the instance is marked DONE with substatus "FULL" and completion 92
    When the user executes undo
    Then the status should be "PENDING"
    And done_substatus should be NULL
    And not_done_substatus should be NULL
    And skip_reason should be NULL
    And skip_note should be NULL
    And completion_percentage should be NULL

  # Cenário 2: Undo de hábito skipped
  Scenario: Undo from SKIPPED clears all skip fields
    Given the instance is skipped with reason "HEALTH" and note "Gripe forte"
    When the user executes undo
    Then the status should be "PENDING"
    And done_substatus should be NULL
    And not_done_substatus should be NULL
    And skip_reason should be NULL
    And skip_note should be NULL
    And completion_percentage should be NULL

  # Cenário 3: Undo preserva TimeLog existente
  Scenario: Undo preserves existing TimeLog records
    Given the instance is marked DONE with substatus "FULL" and completion 92
    And a TimeLog with status "DONE" and duration 3300 seconds exists for the instance
    When the user executes undo
    Then the status should be "PENDING"
    And the TimeLog should still have status "DONE"
    And the TimeLog should still have duration 3300 seconds

  # Cenário 4: Undo preserva identidade da instância
  Scenario: Undo preserves instance identity fields
    Given the instance is marked DONE with substatus "PARTIAL" and completion 75
    When the user executes undo
    Then the status should be "PENDING"
    And the instance habit_id should be unchanged
    And the instance date should be unchanged
    And the instance scheduled_start should be unchanged
    And the instance scheduled_end should be unchanged
