# language: en
Feature: Timer States and Transitions (BR-TIMER-002)
  As a TimeBlock user
  I want to control timer state
  To pause and resume my time tracking

  Background:
    Given an active routine "Test Routine" exists
    And a habit "Gym" exists in the routine
    And an instance of the habit exists for today

  # BR-TIMER-002: start cria estado RUNNING
  Scenario: Start timer creates RUNNING state
    When I start the timer for the instance
    Then the timelog status should be RUNNING
    And the timelog should have start_time filled
    And the timelog should not have end_time

  # BR-TIMER-002: pause muda para PAUSED
  Scenario: Pause timer changes to PAUSED
    Given a RUNNING timer exists for the instance
    When I pause the timer
    Then the timelog status should be PAUSED
    And pause_start should be filled

  # BR-TIMER-002: resume volta para RUNNING
  Scenario: Resume timer returns to RUNNING
    Given a PAUSED timer exists for the instance
    When I resume the timer
    Then the timelog status should be RUNNING
    And pause_start should be empty
    And paused_duration should be greater than zero

  # BR-TIMER-002: stop cria estado DONE
  Scenario: Stop timer creates DONE state
    Given a RUNNING timer exists for the instance
    When I stop the timer
    Then the timelog status should be DONE
    And the timelog should have end_time filled
    And duration_seconds should be calculated

  # BR-TIMER-002: reset cria estado CANCELLED
  Scenario: Reset timer creates CANCELLED state
    Given a RUNNING timer exists for the instance
    When I reset the timer
    Then the timelog status should be CANCELLED
    And the habit instance should remain PENDING

  # BR-TIMER-003: reset com motivo
  Scenario: Reset timer with reason
    Given a RUNNING timer exists for the instance
    When I reset the timer with reason "Started wrong habit"
    Then the timelog status should be CANCELLED
    And cancel_reason should be "Started wrong habit"

  # BR-TIMER-003: reset de sessao especifica
  Scenario: Reset specific DONE session
    Given a DONE timelog exists for the instance
    When I reset the session by timelog id with reason "Wrong habit"
    Then the timelog status should be CANCELLED
    And cancel_reason should be "Wrong habit"

  # BR-TIMER-002: nao pode pausar timer ja pausado
  Scenario: Cannot pause already paused timer
    Given a PAUSED timer exists for the instance
    When I try to pause the timer
    Then it should return error "Timer already paused"

  # BR-TIMER-002: nao pode retomar timer nao pausado
  Scenario: Cannot resume non-paused timer
    Given a RUNNING timer exists for the instance
    When I try to resume the timer
    Then it should return error "Timer not paused"

  # BR-TIMER-003: nao pode resetar sessao ja cancelada
  Scenario: Cannot reset already cancelled session
    Given a CANCELLED timelog exists for the instance
    When I try to reset the session by timelog id
    Then it should return error "Session already cancelled"
