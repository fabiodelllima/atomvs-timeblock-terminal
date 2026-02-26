# language: en
Feature: Timer States (BR-TIMER-002, BR-TIMER-003)
  As a TimeBlock user
  I want to control my timer state
  So that I can track time accurately

  Background:
    Given an active routine "Test Routine" exists
    And a habit "Gym" exists in the routine
    And a pending instance exists for today

  # BR-TIMER-002: Transições de estado

  Scenario: Start timer creates RUNNING state
    When I start the timer for the instance
    Then the timelog should have status "RUNNING"
    And the timelog should have start_time set

  Scenario: Pause timer changes to PAUSED
    Given a RUNNING timer exists
    When I pause the timer
    Then the timelog should have status "PAUSED"
    And the timelog should have pause_start set

  Scenario: Resume timer returns to RUNNING
    Given a PAUSED timer exists
    When I resume the timer
    Then the timelog should have status "RUNNING"
    And the paused time should be accumulated

  Scenario: Cannot pause already paused timer
    Given a PAUSED timer exists
    When I try to pause the timer
    Then it should return error "Timer already paused"

  Scenario: Cannot resume already running timer
    Given a RUNNING timer exists
    When I try to resume the timer
    Then it should return error "Timer already running"

  # BR-TIMER-003: Parar e resetar

  Scenario: Stop finalizes timer with DONE
    Given a RUNNING timer exists
    When I stop the timer
    Then the timelog should have status "DONE"
    And the timelog should have end_time set
    And the instance should have status "DONE"

  Scenario: Stop paused timer finalizes with DONE
    Given a PAUSED timer exists
    When I stop the timer
    Then the timelog should have status "DONE"
    And the paused time should be preserved

  Scenario: Reset cancels timer without saving
    Given a RUNNING timer exists
    When I reset the timer
    Then the timelog should have status "CANCELLED"
    And the instance should remain "PENDING"

  Scenario: Reset with reason stores cancellation reason
    Given a RUNNING timer exists
    When I reset the timer with reason "Started wrong habit"
    Then the timelog should have cancel_reason "Started wrong habit"

  Scenario: Reset specific session
    Given a DONE timelog with id 15 exists
    When I reset session 15 with reason "Duplicate"
    Then timelog 15 should have status "CANCELLED"
    And timelog 15 should have cancel_reason "Duplicate"

  Scenario: Cannot reset already cancelled session
    Given a CANCELLED timelog exists
    When I try to reset the session
    Then it should return error "Session already cancelled"

  Scenario: Stop allows new session on same instance
    Given the instance has a DONE timelog
    When I start the timer for the instance
    Then it should create a new timelog with status "RUNNING"
    And the instance should have 2 timelogs
