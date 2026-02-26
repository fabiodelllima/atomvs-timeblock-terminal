# language: en
# BR-HABITINSTANCE-006: Listagem de instâncias de hábito
Feature: Habit Instance Listing (BR-HABITINSTANCE-006)
  As a TimeBlock user
  I want to list habit instances with filters
  To view my schedule flexibly

  Background:
    Given an active routine "Test Routine" exists
    And a habit "Gym" exists in the routine with schedule 07:00-08:00
    And instances are generated for 7 days

  Scenario: List all instances without filters
    When I list instances without filters
    Then I should receive a list with 7 instances

  Scenario: Filter instances by habit
    Given another habit "Meditation" exists in the routine
    And instances of "Meditation" exist for 7 days
    When I list instances filtering by habit "Gym"
    Then I should receive only "Gym" instances

  Scenario: Filter instances by date range
    When I list instances with date_start today and date_end today+2
    Then I should receive a list with 3 instances

  Scenario: Return empty list when no results
    When I list instances with date_start in distant future
    Then I should receive an empty list
    And the list should not be None
