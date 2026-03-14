# language: en
Feature: Task Lifecycle (BR-TASK-007, BR-TASK-008, BR-TASK-009, BR-TASK-010)
  As a TimeBlock user
  I want tasks with a full lifecycle
  So that I can track completion, cancellation and postponement patterns

  Background:
    Given a task "Dentista" scheduled for tomorrow at 14:00 exists

  # BR-TASK-007: Derivação de status por timestamps

  Scenario: Pending task has no completion or cancellation
    Then the task status should be "pending"

  Scenario: Completed task has completed_datetime set
    When I complete the task
    Then the task status should be "completed"
    And the task should have completed_datetime set

  Scenario: Cancelled task has cancelled_datetime set
    When I cancel the task
    Then the task status should be "cancelled"
    And the task should have cancelled_datetime set
    And the task should still exist in the database

  Scenario: Overdue task has scheduled_datetime in the past
    Given a task "Relatório" scheduled for yesterday at 09:00 exists
    Then the task "Relatório" status should be "overdue"

  Scenario: Cancelled overrides completed
    When I complete the task
    And I cancel the task
    Then the task status should be "cancelled"

  # BR-TASK-008: Rastreamento de adiamento

  Scenario: New task has original_scheduled_datetime equal to scheduled
    Then the task original_scheduled_datetime should equal scheduled_datetime

  Scenario: Postponing increments counter
    When I reschedule the task to 3 days later
    Then the task postponement_count should be 1
    And the task original_scheduled_datetime should not change

  Scenario: Rescheduling to earlier date does not increment counter
    When I reschedule the task to 1 day earlier
    Then the task postponement_count should be 0

  Scenario: Multiple postponements accumulate
    When I reschedule the task to 2 days later
    And I reschedule the task to 3 days later
    Then the task postponement_count should be 2

  # BR-TASK-009: Soft delete

  Scenario: Cancelled task excluded from pending list
    When I cancel the task
    Then the pending tasks list should not contain "Dentista"

  Scenario: Cancelled task included in all tasks list
    When I cancel the task
    Then the all tasks list should contain "Dentista"

  Scenario: Reopen clears cancellation
    When I cancel the task
    And I reopen the task
    Then the task status should be "pending"
    And the task should not have cancelled_datetime set

  # BR-TASK-010: Métricas de lifecycle

  Scenario: Completed on time
    When I complete the task
    Then the task should be marked as completed_on_time

  Scenario: Completed late
    Given a task "Imposto" scheduled for yesterday at 09:00 exists
    When I complete the task "Imposto"
    Then the task "Imposto" should have days_late greater than 0

  Scenario: Postponed task metrics
    When I reschedule the task to 5 days later
    Then the task days_postponed should be 5
    And the task was_postponed should be true
