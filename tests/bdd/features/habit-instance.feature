# language: en
Feature: HabitInstance States and Transitions
  As a TimeBlock system
  I want to manage habit instance states
  So that I can track execution and calculate metrics

  Background:
    Given an active routine "Rotina Matinal" exists
    And a habit "Academia" with expected duration of 90 minutes exists

  # BR-HABIT-INSTANCE-001: Transições de status
  Scenario: Transition PENDING to DONE via timer stop
    Given an instance with status "PENDING" exists
    When the timer is started
    And the timer is stopped after 90 minutes
    Then the status changes to "DONE"
    And the done_substatus is calculated

  Scenario: Transition PENDING to NOT_DONE via skip
    Given an instance with status "PENDING" exists
    When the user runs "habit skip Academia --reason HEALTH"
    Then the status changes to "NOT_DONE"
    And the not_done_substatus is "SKIPPED_JUSTIFIED"

  Scenario: Transition PENDING to NOT_DONE via timeout (48h)
    Given an instance with status "PENDING" created 49 hours ago exists
    When the timeout job runs
    Then the status changes to "NOT_DONE"
    And the not_done_substatus is "IGNORED"

  Scenario: Forbidden transitions from DONE
    Given an instance with status "DONE" exists
    When an attempt to change to "PENDING" is made
    Then the system returns error "Status DONE é final"

    When an attempt to change to "NOT_DONE" is made
    Then the system returns error "Status DONE é final"

  Scenario: Forbidden transitions from NOT_DONE
    Given an instance with status "NOT_DONE" exists
    When an attempt to change to "PENDING" is made
    Then the system returns error "Status NOT_DONE é final"

    When an attempt to change to "DONE" is made
    Then the system returns error "Status NOT_DONE é final"

  # BR-HABIT-INSTANCE-002: Atribuição de substatus
  Scenario: DONE always has done_substatus
    Given the instance transitions to "DONE"
    Then done_substatus CANNOT be NULL
    And not_done_substatus must be NULL

  Scenario: NOT_DONE always has not_done_substatus
    Given the instance transitions to "NOT_DONE"
    Then not_done_substatus CANNOT be NULL
    And done_substatus must be NULL

  Scenario: PENDING has both substatus NULL
    Given the instance has status "PENDING"
    Then done_substatus must be NULL
    And not_done_substatus must be NULL

  Scenario: Substatus are mutually exclusive
    Given the instance has status "DONE"
    When an attempt to set not_done_substatus is made
    Then the system returns error "Substatus mutuamente exclusivos"

  # BR-HABIT-INSTANCE-003: Thresholds de completion
  Scenario: EXCESSIVE when completion > 150%
    Given the expected duration is 90 minutes
    When the actual duration is 180 minutes
    Then completion is 200%
    And done_substatus is "EXCESSIVE"
    And the system shows a warning about impact

  Scenario: OVERDONE when completion 110-150%
    Given the expected duration is 90 minutes
    When the actual duration is 100 minutes
    Then completion is 111%
    And done_substatus is "OVERDONE"
    And the system shows info about recurrence

  Scenario: FULL when completion 90-110%
    Given the expected duration is 90 minutes
    When the actual duration is 90 minutes
    Then completion is 100%
    And done_substatus is "FULL"
    And the system shows positive feedback

  Scenario: PARTIAL when completion < 90%
    Given the expected duration is 90 minutes
    When the actual duration is 60 minutes
    Then completion is 67%
    And done_substatus is "PARTIAL"
    And the system maintains the streak

  Scenario Outline: Threshold edge cases
    Given the expected duration is 90 minutes
    When the actual duration is <real> minutes
    Then completion is <percentage>%
    And done_substatus is "<substatus>"

    Examples:
      | real | percentage | substatus  |
      | 136  | 151.11     | EXCESSIVE  |
      | 135  | 150.00     | EXCESSIVE  |
      | 134  | 148.89     | OVERDONE   |
      | 100  | 111.11     | OVERDONE   |
      | 99   | 110.00     | OVERDONE   |
      | 98   | 108.89     | FULL       |
      | 90   | 100.00     | FULL       |
      | 81   | 90.00      | FULL       |
      | 80   | 88.89      | PARTIAL    |

  # BR-HABIT-INSTANCE-004: Cálculo de streak com substatus
  Scenario: Any DONE maintains streak
    Given the current streak is 5 days
    And the last instance was DONE with substatus "<substatus>"
    When a new instance is marked as DONE
    Then the streak increments to 6 days

    Examples:
      | substatus  |
      | EXCESSIVE  |
      | OVERDONE   |
      | FULL       |
      | PARTIAL    |

  Scenario: Any NOT_DONE breaks streak
    Given the current streak is 14 days
    And a new instance is marked as NOT_DONE with substatus "<substatus>"
    Then the streak resets to 0 days

    Examples:
      | substatus            |
      | SKIPPED_JUSTIFIED    |
      | SKIPPED_UNJUSTIFIED  |
      | IGNORED              |

  Scenario: EXCESSIVE maintains streak but warns about impact
    Given the current streak is 12 days
    When the instance is marked as DONE (EXCESSIVE)
    Then the streak increments to 13 days
    And the system shows a warning:
      """
      [WARN] Academia ultrapassou meta em Xmin

      Impacto na rotina:
        - <habit>: PERDIDO/ATRASADO
      """

  # BR-HABIT-INSTANCE-005: Atribuição automática de ignored
  Scenario: PENDING instance less than 48h is not ignored
    Given the instance was created 24 hours ago
    When the timeout job runs
    Then the status remains "PENDING"

  Scenario: PENDING instance over 48h is ignored
    Given the instance was created 49 hours ago
    And the status is "PENDING"
    When the timeout job runs
    Then the status changes to "NOT_DONE"
    And not_done_substatus is "IGNORED"
    And the ignored_at timestamp is recorded

  Scenario: Only PENDING instances are checked
    Given instances with status "DONE" and "NOT_DONE" exist
    When the timeout job runs
    Then only "PENDING" instances are processed
    And "DONE" and "NOT_DONE" instances are not altered

  Scenario: User action before 48h prevents IGNORED
    Given the instance was created 30 hours ago
    When the user runs "habit skip Academia --reason WORK"
    Then the status is "NOT_DONE"
    And not_done_substatus is "SKIPPED_JUSTIFIED"
    And the timeout job does NOT mark it as IGNORED

  # BR-HABIT-INSTANCE-006: Análise de impacto em EXCESSIVE/OVERDONE
  Scenario: EXCESSIVE with impact on subsequent habits
    Given Academia is scheduled for 07:00-08:30 (90min)
    And Trabalho is scheduled for 09:00-12:00 (180min)
    And Inglês is scheduled for 13:00-14:00 (60min)
    When Academia ends at 10:00 (180min actual)
    Then done_substatus is "EXCESSIVE"
    And the system detects impact:
      | habit    | impact    |
      | Trabalho | PERDIDO   |
      | Inglês   | ATRASADO  |
    And the system suggests "Ajustar meta de Academia para 2h?"

  Scenario: OVERDONE without impact (sufficient gap)
    Given Academia is scheduled for 07:00-08:30 (90min)
    And Inglês is scheduled for 14:00-15:00 (60min)
    When Academia ends at 09:00 (120min actual)
    Then done_substatus is "OVERDONE"
    And no habit was affected
    And the system shows info:
      """
      [INFO] Acima da meta. Frequente? Considere ajustar para 2h.
      """

  Scenario: FULL does not trigger impact analysis
    Given Academia ends exactly on time (90min)
    When done_substatus is "FULL"
    Then impact analysis is NOT executed

  Scenario: PARTIAL does not trigger impact analysis
    Given Academia ends before the scheduled time (60min)
    When done_substatus is "PARTIAL"
    Then impact analysis is NOT executed
