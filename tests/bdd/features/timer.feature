# language: en
Feature: Timer and Time Tracking
  As a TimeBlock user
  I want to track time spent on habits
  So that I can calculate completion % and substatus

  Background:
    Given a habit "Academia" with expected duration of 90 minutes exists

  # BR-TIMER-001: Restrição de timer ativo único
  Scenario: Only one active timer at a time
    Given the timer for "Academia" is RUNNING
    When an attempt to start the timer for "Meditação" is made
    Then the system returns error:
      """
      [ERROR] Timer já ativo: Academia (45min decorridos)

      Opções:
        [1] Pausar Academia e iniciar Meditação
        [2] Cancelar Academia (reset) e iniciar Meditação
        [3] Continuar com Academia
      """

  Scenario: PAUSED timer blocks new start
    Given the timer for "Academia" is PAUSED
    When an attempt to start the timer for "Meditação" is made
    Then the system returns error "Timer já ativo (pausado)"

  Scenario: Timer after stop does NOT block new start
    Given the timer for "Academia" was stopped
    When the user runs "timer start Meditação"
    Then the new timer starts successfully
    And the previous timer is no longer active

  Scenario: Multiple sessions of the same habit allowed
    Given the timer for "Academia" was stopped (session 1: 60min)
    When the user runs "timer start Academia"
    Then the new timer starts successfully (session 2)
    And both sessions will be accumulated

  # BR-TIMER-002: Transições de estado
  Scenario: Valid states: only RUNNING and PAUSED
    When the system checks the TimerStatus enum
    Then only 2 states exist:
      | state   |
      | RUNNING |
      | PAUSED  |

  Scenario: Normal flow (start, pause, resume, stop)
    When the user runs "timer start Academia"
    Then the status is RUNNING

    When the user runs "timer pause"
    Then the status is PAUSED

    When the user runs "timer resume"
    Then the status is RUNNING

    When the user runs "timer stop"
    Then the timer no longer exists (finalized)
    And the session was saved as DONE

  Scenario: Stop saves session and marks DONE
    Given the timer has been RUNNING for 90 minutes
    When the user runs "timer stop"
    Then the session is saved with duration = 90
    And the instance is marked as DONE
    And done_substatus is calculated

  Scenario: Reset cancels without saving
    Given the timer has been RUNNING for 30 minutes
    When the user runs "timer reset"
    Then the timer no longer exists (cancelled)
    And the session is NOT saved
    And the instance remains PENDING

  Scenario: Pause only works when RUNNING
    Given the timer is PAUSED
    When an attempt to run "timer pause" is made
    Then the system returns error "Timer já está pausado"

  Scenario: Resume only works when PAUSED
    Given the timer is RUNNING
    When an attempt to run "timer resume" is made
    Then the system returns error "Timer não está pausado"

  Scenario: Stop works when RUNNING or PAUSED
    Given the timer is in state "<state>"
    When the user runs "timer stop"
    Then the session is saved successfully

    Examples:
      | state   |
      | RUNNING |
      | PAUSED  |

  Scenario: Reset works when RUNNING or PAUSED
    Given the timer is in state "<state>"
    When the user runs "timer reset"
    Then the timer is cancelled without saving

    Examples:
      | state   |
      | RUNNING |
      | PAUSED  |

  # BR-TIMER-003: Múltiplas sessões no mesmo dia
  Scenario: Two sessions accumulate duration (PARTIAL to OVERDONE)
    Given the user completes session 1 of "Academia": 60min
    When the user completes session 2 of "Academia": 35min
    Then the total duration is 95min
    And completion is 106%
    And done_substatus is OVERDONE

  Scenario: CLI shows breakdown of multiple sessions
    Given the user completed 2 sessions of "Academia"
    When the last "timer stop" is executed
    Then the system shows:
      """
      ✓ Sessão 2 completa: 35min

      ╔════════════════════════════════╗
      ║  TOTAL DO DIA: Academia        ║
      ╠════════════════════════════════╣
      ║  Sessões: 2                    ║
      ║  Tempo: 95min (106% da meta)   ║
      ║  Status: DONE (OVERDONE)       ║
      ╚════════════════════════════════╝
      """

  Scenario: Three sessions lead to EXCESSIVE
    When the user completes sessions of "Academia":
      | session | duration |
      | 1       | 60min    |
      | 2       | 40min    |
      | 3       | 70min    |
    Then the total duration is 170min
    And completion is 189%
    And done_substatus is EXCESSIVE

  Scenario: Each stop saves an independent session
    When the user executes the flow:
      | command              | result            |
      | timer start Academia | Timer started     |
      | timer stop           | Session 1 saved   |
      | timer start Academia | Timer started     |
      | timer stop           | Session 2 saved   |
    Then 2 independent sessions exist
    And both have recorded duration

  Scenario: Instance marked DONE after first session
    Given the instance is PENDING
    When the first session is completed (60min)
    Then the instance is marked as DONE
    And done_substatus is PARTIAL (67%)

    When the second session is added (35min)
    Then done_substatus is updated to OVERDONE (106%)

  # BR-TIMER-004: Validação de log manual
  Scenario: Manual log with times (start + end)
    When the user runs "habit log Academia --start 07:00 --end 08:30"
    Then the calculated duration is 90min
    And completion is 100%
    And done_substatus is FULL

  Scenario: Manual log with duration
    When the user runs "habit log Academia --duration 90"
    Then the duration is 90min
    And completion is 100%

  Scenario: Validation: start < end
    When the user runs "habit log Academia --start 08:00 --end 07:00"
    Then the system returns error "Horário de fim antes do início"

  Scenario: Validation: positive duration
    When the user runs "habit log Academia --duration -10"
    Then the system returns error "Duração deve ser positiva"

  Scenario: Validation: only one method
    When the user runs "habit log Academia --start 07:00 --end 08:00 --duration 60"
    Then the system returns error "Use start+end OU duration, não ambos"

  Scenario: Validation: blocks if timer is active
    Given the timer for "Academia" is RUNNING
    When the user runs "habit log Academia --duration 90"
    Then the system returns error:
      """
      [ERROR] Timer ativo para Academia
              Stop timer primeiro: timer stop
      """

  Scenario: Add new manual session to DONE habit
    Given "Academia" already has 1 session (timer): 60min
    When the user runs "habit log Academia --duration 30"
    Then the system asks:
      """
      Habit já completo (1 sessão: 60min).
      Adicionar nova sessão? [y/N]:
      """
    And upon confirmation, a new session is added
    And the accumulated total is 90min

  # BR-TIMER-005: Cálculo de completion percentage
  Scenario: Completion formula
    Given the expected duration is 90min
    When the accumulated actual duration is <real>min
    Then completion is <percentage>%

    Examples:
      | real | percentage |
      | 180  | 200.00     |
      | 135  | 150.00     |
      | 100  | 111.11     |
      | 90   | 100.00     |
      | 60   | 66.67      |

  Scenario: Substatus based on thresholds
    Given the expected duration is 90min
    When completion is <percentage>%
    Then done_substatus is "<substatus>"

    Examples:
      | percentage | substatus  |
      | 200        | EXCESSIVE  |
      | 150        | EXCESSIVE  |
      | 149        | OVERDONE   |
      | 111        | OVERDONE   |
      | 110        | OVERDONE   |
      | 109        | FULL       |
      | 100        | FULL       |
      | 90         | FULL       |
      | 89         | PARTIAL    |
      | 67         | PARTIAL    |

  Scenario: Multiple sessions accumulated in calculation
    Given the following sessions exist:
      | type  | duration |
      | timer | 60min    |
      | timer | 25min    |
      | log   | 10min    |
    When completion is calculated
    Then the accumulated total is 95min
    And completion is 106%
    And done_substatus is OVERDONE

  Scenario: Pauses deducted from total time
    Given the timer started at 07:00
    And the timer was paused from 07:30 to 07:40 (10min)
    And the timer was paused from 08:10 to 08:15 (5min)
    And the timer stopped at 08:45
    When completion is calculated
    Then total elapsed time is 105min
    And pauses total 15min
    And effective duration is 90min
    And completion is 100%

  Scenario: Rounding to 2 decimal places
    Given the expected duration is 90min
    When the actual duration is 85min
    Then completion is 94.44%
    And not 94.444444...%

  # BR-TIMER-006: Rastreamento de pausas
  Scenario: Pausing creates a TimeLog
    Given the timer is RUNNING
    When the user runs "timer pause"
    Then a TimeLog is created with:
      | field       | value              |
      | timer_id    | <timer id>         |
      | pause_start | <current timestamp>|
      | pause_end   | NULL               |
      | duration    | NULL               |

  Scenario: Resuming finalizes the TimeLog
    Given the timer has been PAUSED for 10 minutes
    When the user runs "timer resume"
    Then the TimeLog is updated with:
      | field       | value              |
      | pause_end   | <current timestamp>|
      | duration    | 10                 |

  Scenario: Multiple pauses tracked
    When the user executes the flow:
      | command      | time  | result                |
      | timer start  | 07:00 | Timer started         |
      | timer pause  | 07:30 | TimeLog 1 created     |
      | timer resume | 07:40 | TimeLog 1 finalized   |
      | timer pause  | 08:10 | TimeLog 2 created     |
      | timer resume | 08:15 | TimeLog 2 finalized   |
      | timer stop   | 08:45 | Timer finalized       |
    Then 2 TimeLogs exist:
      | log | pause_start | pause_end | duration |
      | 1   | 07:30       | 07:40     | 10min    |
      | 2   | 08:10       | 08:15     | 5min     |

  Scenario: CLI shows pauses in final output
    Given the timer had 2 pauses (10min + 5min)
    When the user runs "timer stop"
    Then the system shows:
      """
      ✓ SESSÃO COMPLETA!
      ╔════════════════════════════════════════╗
      ║ Academia (14/11/2025)                  ║
      ╠════════════════════════════════════════╣
      ║ Programado: 07:00 → 08:30 (90min)      ║
      ║ Real: 07:00 → 08:45 (105min total)     ║
      ╠════════════════════════════════════════╣
      ║ Pausas: 2x (15min total)               ║
      ║   1. 07:30-07:40 (10min)               ║
      ║   2. 08:10-08:15 (5min)                ║
      ╠════════════════════════════════════════╣
      ║ Tempo efetivo: 90min                   ║
      ║ Completion: 100%                       ║
      ║ Status: DONE (FULL)                    ║
      ╚════════════════════════════════════════╝
      """

  Scenario: Pauses with optional reason
    When the user pauses the timer
    And adds reason "Telefone tocou"
    Then the TimeLog has reason = "Telefone tocou"

  Scenario: Effective duration deducting pauses
    Given the timer ran from 07:00 to 08:00 (60min)
    And had pauses of 5min + 3min + 2min
    When effective duration is calculated
    Then raw time is 60min
    And pauses total 10min
    And effective duration is 50min
