Feature: Manual Time Logging (BR-TIMER-007)
  As a TimeBlock user
  I want to log time manually without using a timer
  So that I can record activities I forgot to track

  Background:
    Given an active routine "Morning Routine" exists
    And a habit "Meditation" with 60 minutes duration exists
    And a pending instance for today exists

  # Modo Intervalo
  Scenario: Log time using start and end times
    When I log time with start "07:00" and end "08:00"
    Then a TimeLog should be created with duration 3600 seconds
    And the instance should be marked as DONE
    And the instance should have completion 100%

  Scenario: Log partial time using interval
    When I log time with start "07:00" and end "07:30"
    Then a TimeLog should be created with duration 1800 seconds
    And the instance should have completion 50%
    And the instance should have substatus PARTIAL

  # Modo Duração
  Scenario: Log time using duration in minutes
    When I log time with duration 60 minutes
    Then a TimeLog should be created with duration 3600 seconds
    And the instance should be marked as DONE
    And the instance should have substatus FULL

  Scenario: Log overdone time using duration
    When I log time with duration 90 minutes
    Then a TimeLog should be created with duration 5400 seconds
    And the instance should have completion 150%
    And the instance should have substatus OVERDONE

  # Validações
  Scenario: Reject when start is after end
    When I try to log time with start "09:00" and end "08:00"
    Then I should receive a validation error "start must be before end"

  Scenario: Reject when duration is zero or negative
    When I try to log time with duration 0 minutes
    Then I should receive a validation error "duration must be positive"

  Scenario: Reject when mixing interval and duration modes
    When I try to log time with start "07:00" and end "08:00" and duration 60
    Then I should receive a validation error "cannot mix interval and duration modes"

  Scenario: Reject when interval is incomplete
    When I try to log time with only start "07:00"
    Then I should receive a validation error "start requires end"
