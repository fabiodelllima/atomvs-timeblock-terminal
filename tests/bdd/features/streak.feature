# language: en
Feature: Streak Calculation and Management
  As a TimeBlock user
  I want to track my consistency in habits
  So that I maintain motivation and track progress

  # Baseado em "Atomic Habits" (James Clear)
  # Filosofia: Consistência > Perfeição

  Background:
    Given a habit "Academia" in the active routine exists

  # BR-STREAK-001: Algoritmo de cálculo
  Scenario: Calculate streak of consecutive days
    Given instances with the following statuses exist:
      | date       | status   |
      | 2025-11-14 | DONE     |
      | 2025-11-13 | DONE     |
      | 2025-11-12 | DONE     |
      | 2025-11-11 | NOT_DONE |
      | 2025-11-10 | DONE     |
    When the system calculates the streak
    Then the current streak is 3 days

  Scenario: Streak is zero when last instance is NOT_DONE
    Given instances with the following statuses exist:
      | date       | status   |
      | 2025-11-14 | NOT_DONE |
      | 2025-11-13 | DONE     |
      | 2025-11-12 | DONE     |
    When the system calculates the streak
    Then the current streak is 0 days

  Scenario: PENDING does not affect streak calculation
    Given instances with the following statuses exist:
      | date       | status   |
      | 2025-11-16 | PENDING  |
      | 2025-11-15 | PENDING  |
      | 2025-11-14 | DONE     |
      | 2025-11-13 | DONE     |
      | 2025-11-12 | NOT_DONE |
    When the system calculates the streak
    Then the current streak is 2 days
    And PENDING instances are ignored

  Scenario: Streak is zero when no DONE instances exist
    Given the habit was created today
    And there are no instances with status DONE
    When the system calculates the streak
    Then the current streak is 0 days

  Scenario: Counting from most recent to oldest
    Given instances of Academia exist:
      | date       | status   |
      | 2025-11-14 | DONE     |
      | 2025-11-13 | DONE     |
      | 2025-11-12 | DONE     |
    When the system calculates the streak starting from today
    Then it traverses instances from 14/11 to 13/11 to 12/11
    And stops at the first NOT_DONE or end of list

  # BR-STREAK-002: Condições de quebra
  Scenario: NOT_DONE always breaks streak (fundamental rule)
    Given the current streak is 20 days
    When a new instance is marked as NOT_DONE
    Then the streak resets to 0 days
    And the NOT_DONE substatus does not matter

  Scenario: SKIPPED_JUSTIFIED breaks streak (LOW psychological impact)
    Given the current streak is 14 days
    When the instance is marked as SKIPPED_JUSTIFIED (HEALTH)
    Then the streak resets to 0 days
    And the system shows compassionate feedback:
      """
      ✗ Academia pulada (justificado: Saúde)
        Streak quebrado: 14 → 0 dias
        Motivo registrado: Consulta médica

      Continue amanhã para recomeçar streak!
      """

  Scenario: SKIPPED_UNJUSTIFIED breaks streak (MEDIUM psychological impact)
    Given the current streak is 14 days
    When the instance is marked as SKIPPED_UNJUSTIFIED
    Then the streak resets to 0 days
    And the system shows moderate warning:
      """
      ✗ Academia pulada (sem justificativa)
        Streak quebrado: 14 → 0 dias

      [WARN] Skip sem justificativa.
             Adicionar motivo? [Y/n]:
      """

  Scenario: IGNORED breaks streak (HIGH psychological impact)
    Given the current streak is 7 days
    And the habit was ignored 3 times this month
    When the instance is marked as IGNORED
    Then the streak resets to 0 days
    And the system shows a strong alert:
      """
      [WARN] Academia ignorada (sem ação consciente)
             Streak quebrado: 7 → 0 dias

             3 ignores este mês.
             Considere ajustar horário ou meta.
      """

  Scenario: All NOT_DONE substatus break equally
    Given the current streak is 10 days
    When the instance is marked as NOT_DONE with substatus "<substatus>"
    Then the streak resets to 0 days

    Examples:
      | substatus            |
      | SKIPPED_JUSTIFIED    |
      | SKIPPED_UNJUSTIFIED  |
      | IGNORED              |

  # BR-STREAK-003: Condições de manutenção
  Scenario: DONE always maintains streak (fundamental rule)
    Given the current streak is 5 days
    When a new instance is marked as DONE
    Then the streak increments to 6 days
    And the DONE substatus does not matter

  Scenario: PARTIAL maintains streak without penalty
    Given the current streak is 5 days
    When the instance is marked as DONE (PARTIAL - 67%)
    Then the streak increments to 6 days
    And the system shows encouraging feedback:
      """
      ✓ Sessão completa!
        Tempo: 60min (67% da meta)
        Status: DONE (PARTIAL)
        Streak: 6 dias ✓

      [INFO] Abaixo da meta, mas streak mantido!
      """

  Scenario: OVERDONE maintains streak with monitoring
    Given the current streak is 8 days
    When the instance is marked as DONE (OVERDONE - 111%)
    Then the streak increments to 9 days
    And the system shows info:
      """
      ✓ Sessão completa!
        Tempo: 100min (111% da meta)
        Status: DONE (OVERDONE)
        Streak: 9 dias ✓

      [INFO] Acima da meta. Frequente? Considere ajustar.
      """

  Scenario: EXCESSIVE maintains streak with impact warning
    Given the current streak is 12 days
    And Academia exceeded its goal affecting Trabalho and Inglês
    When the instance is marked as DONE (EXCESSIVE - 200%)
    Then the streak increments to 13 days
    And the system shows warning:
      """
      ✓ Sessão completa!
        Tempo: 180min (200% da meta)
        Status: DONE (EXCESSIVE)
        Streak: 13 dias ✓

      [WARN] Academia ultrapassou meta em 90min

      Impacto na rotina:
        - Trabalho: PERDIDO
        - Inglês: ATRASADO 1h

      Sugestão: Ajustar meta para 2h?
      """

  Scenario: FULL maintains streak with positive feedback
    Given the current streak is 30 days
    When the instance is marked as DONE (FULL - 100%)
    Then the streak increments to 31 days
    And the system shows celebration:
      """
      ✓ Sessão completa!
        Tempo: 90min (100% da meta)
        Status: DONE (FULL)

      ╔════════════════════════════════════════╗
      ║  MILESTONE: 31 DIAS CONSECUTIVOS!      ║
      ╠════════════════════════════════════════╣
      ║  Parabéns! Hábito consolidado.         ║
      ║  Continue assim!                       ║
      ╚════════════════════════════════════════╝
      """

  Scenario: All DONE substatus maintain equally
    Given the current streak is 7 days
    When the instance is marked as DONE with substatus "<substatus>"
    Then the streak increments to 8 days

    Examples:
      | substatus  |
      | EXCESSIVE  |
      | OVERDONE   |
      | FULL       |
      | PARTIAL    |

  # BR-STREAK-004: Feedback psicológico por substatus
  Scenario: Differentiated feedback by NOT_DONE substatus
    When the instance breaks the streak with substatus "<substatus>"
    Then the feedback tone is "<tone>"
    And the psychological impact is "<impact>"

    Examples:
      | substatus            | tone             | impact |
      | SKIPPED_JUSTIFIED    | Compassionate    | Low    |
      | SKIPPED_UNJUSTIFIED  | Moderate         | Medium |
      | IGNORED              | Strong Alert     | High   |

  Scenario: SKIPPED_JUSTIFIED uses compassionate language
    Given the streak is broken by SKIPPED_JUSTIFIED
    Then the feedback contains phrases like:
      | phrase                             |
      | Tudo bem, acontece                 |
      | Continue amanhã                    |
      | Motivo registrado                  |
    And does NOT contain phrases like:
      | phrase                             |
      | Você falhou                        |
      | Streak perdido                     |
      | Que pena                           |

  Scenario: SKIPPED_UNJUSTIFIED offers to add justification
    Given the streak is broken by SKIPPED_UNJUSTIFIED
    Then the system asks "Adicionar motivo? [Y/n]"
    And offers command: "habit skip <id> --add-reason"

  Scenario: IGNORED uses strong warning
    Given the streak is broken by IGNORED
    Then the system uses [WARN] symbol in red
    And asks "Hábito está consolidado?"
    And suggests "Ajustar horário ou meta?"

  Scenario: Reports with break analysis
    When the user runs "report habit Academia --period 30"
    Then the system shows breakdown:
      """
      Quebras este mês: 3x
        ├─ Skipped (justified): 2x  (Trabalho, Saúde)
        ├─ Skipped (unjust.): 0x
        └─ Ignored: 1x              [WARN]

      [INFO] Quebras justificadas são normais (67% deste mês)
      [WARN] 1 ignore detectado - atenção ao engajamento
      """

  Scenario: Milestones are celebrated
    When the streak reaches "<milestone>" days
    Then the system shows a special celebration

    Examples:
      | milestone |
      | 7         |
      | 21        |
      | 30        |
      | 60        |
      | 90        |
      | 365       |

  Scenario: Feedback adapted to context
    Given the user has a history of justified skips (80%)
    When a new break by SKIPPED_JUSTIFIED occurs
    Then the feedback acknowledges the pattern:
      """
      ✗ Academia pulada (justificado)
        Streak: 5 → 0 dias

      Suas quebras são sempre justificadas ✓
      Padrão saudável de flexibilidade.
      """
