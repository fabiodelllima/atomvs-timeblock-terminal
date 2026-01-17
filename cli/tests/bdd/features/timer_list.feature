Feature: TimeLog Listing (BR-TIMER-008)
  As a TimeBlock user
  I want to list timelogs with filters
  To view my time tracking history

  Background:
    Given an active routine "Test Routine" exists
    And a habit "Gym" exists in the routine
    And instances are generated for 3 days
    And timelogs exist for the instances

  Scenario: List all timelogs without filters
    When I list timelogs without filters
    Then I should receive a list with 3 timelogs

  Scenario: Filter timelogs by instance
    When I list timelogs filtering by the first instance
    Then I should receive only timelogs from the first instance

  Scenario: Filter timelogs by date range
    When I list timelogs with date_start today and date_end today
    Then I should receive a list with 1 timelog

  Scenario: Return empty list when no results
    When I list timelogs with date_start in distant future
    Then I should receive an empty timelog list
    And the timelog list should not be None
