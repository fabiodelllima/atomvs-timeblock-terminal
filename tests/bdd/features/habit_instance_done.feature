# language: en
# BR-HABITINSTANCE-002: Substatus obrigatório para status finais
Feature: Habit Instance Done with Substatus (BR-HABITINSTANCE-002)
  As a TimeBlock user
  I want to mark a habit as done with a specific substatus
  So that the system records how well I completed the habit

  Background:
    Given a routine "Rotina Matinal" exists
    And a habit "Exercício" is scheduled for today at 08:00-09:00
    And a HabitInstance with status "PENDING" exists

  # Cenário 1: Done com FULL substatus
  Scenario: Done with FULL substatus
    When the user marks the instance as done with substatus "FULL"
    Then the status should be "DONE"
    And done_substatus should be "FULL"
    And not_done_substatus should be NULL
    And skip_reason should be NULL
    And skip_note should be NULL

  # Cenário 2: Done com PARTIAL substatus
  Scenario: Done with PARTIAL substatus
    When the user marks the instance as done with substatus "PARTIAL"
    Then the status should be "DONE"
    And done_substatus should be "PARTIAL"

  # Cenário 3: Done limpa dados de skip prévio
  Scenario: Done clears previous skip data
    Given the instance is skipped with reason "HEALTH" and note "Gripe forte"
    When the user marks the instance as done with substatus "FULL"
    Then the status should be "DONE"
    And done_substatus should be "FULL"
    And not_done_substatus should be NULL
    And skip_reason should be NULL
    And skip_note should be NULL
    And completion_percentage should be NULL

  # Cenário 4: Done em instância inexistente
  Scenario: Done on nonexistent instance returns None
    When the user marks instance 99999 as done with substatus "FULL"
    Then the result should be None
