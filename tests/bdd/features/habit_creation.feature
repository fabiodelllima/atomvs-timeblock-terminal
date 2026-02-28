# language: en
# BR-HABIT-001: Criação de hábitos em rotinas
Feature: Habit Creation in Routines
  As a TimeBlock user
  I want to create habits with specific schedules
  So that I can organize my daily routine

  Background:
    Given a routine called "Matinal" exists

  Scenario: Create habit with valid data
    When I create a habit with the following data:
      | Field          | Value             |
      | Title          | Exercício Matinal |
      | Start Time     | 06:00             |
      | End Time       | 07:00             |
      | Recurrence     | EVERYDAY          |
    Then the habit should be created successfully
    And the habit should have a unique ID
    And the title should be "Exercício Matinal"

  Scenario: Reject empty title
    When I try to create a habit with an empty title
    Then the system should reject with error "cannot be empty"

  Scenario: Reject invalid schedule
    When I try to create a habit with:
      | Field          | Value    |
      | Title          | Invalid  |
      | Start Time     | 07:00    |
      | End Time       | 06:00    |
    Then the system should reject with error "Start time must be before end time"
