# language: en
Feature: Habit Skip with Justification
  As a TimeBlock user
  I want to skip habits when necessary
  So that I maintain flexibility without losing tracking

  Background:
    Given an active routine "Rotina Matinal" exists
    And a habit "Academia" is scheduled for today at 07:00

  # BR-HABIT-SKIP-001: Categorização de skip com enum
  Scenario: Skip with valid category (HEALTH)
    When the user runs "habit skip Academia --reason HEALTH --note 'Consulta médica'"
    Then habit "Academia" has status "NOT_DONE"
    And habit "Academia" has substatus "SKIPPED_JUSTIFIED"
    And the skip_reason is "saude"
    And the skip_note is "Consulta médica"
    And the streak for "Academia" is broken

  Scenario: Skip with all 8 categories
    When the user tries skip with reason "HEALTH"
    Then the skip_reason should be "saude"

    When the user tries skip with reason "WORK"
    Then the skip_reason should be "trabalho"

    When the user tries skip with reason "FAMILY"
    Then the skip_reason should be "familia"

    When the user tries skip with reason "TRAVEL"
    Then the skip_reason should be "viagem"

    When the user tries skip with reason "WEATHER"
    Then the skip_reason should be "clima"

    When the user tries skip with reason "LACK_RESOURCES"
    Then the skip_reason should be "falta_recursos"

    When the user tries skip with reason "EMERGENCY"
    Then the skip_reason should be "emergencia"

    When the user tries skip with reason "OTHER"
    Then the skip_reason should be "outro"

  Scenario: Skip with invalid category
    When the user runs "habit skip Academia --reason INVALID"
    Then the system returns error "Categoria inválida"
    And habit "Academia" remains with status "PENDING"

  # BR-HABIT-SKIP-002: Campos de skip
  Scenario: Skip note limited to 200 characters
    Given the skip_note has 200 characters
    When the user runs skip with that note
    Then the skip is recorded successfully

    Given the skip_note has 201 characters
    When the user runs skip with that note
    Then the system returns error "skip_note deve ter no máximo 200 caracteres"

  Scenario: Skip note is optional
    When the user runs "habit skip Academia --reason HEALTH"
    Then the habit is marked as SKIPPED_JUSTIFIED
    And the skip_reason is "saude"
    And the skip_note is NULL

  Scenario: Skip fields NULL when not skipped
    Given habit "Academia" has status "DONE"
    Then the skip_reason should be NULL
    And the skip_note should be NULL

  # BR-HABIT-SKIP-003: Prazo para justificar skip
  Scenario: Justify skip within 24h
    Given the user skipped without justification at 08:00 on 14/11
    And it is now 18:00 on 14/11 (10h later)
    When the user runs "habit skip Academia --add-reason WORK"
    Then the substatus changes from "SKIPPED_UNJUSTIFIED" to "SKIPPED_JUSTIFIED"
    And the skip_reason is "trabalho"

  Scenario: Justify skip after 24h (deadline expired)
    Given the user skipped without justification at 08:00 on 14/11
    And it is now 09:00 on 15/11 (25h later)
    When the user runs "habit skip Academia --add-reason WORK"
    Then the system returns error "Prazo de 24h expirado"
    And the substatus remains "SKIPPED_UNJUSTIFIED"

  Scenario: Skip without justification shows deadline
    When the user runs "habit skip Academia --no-reason"
    Then the system displays message:
      """
      [WARN] Skip sem justificativa
             Prazo para justificar: até <data + 24h>
      """
    And the substatus is "SKIPPED_UNJUSTIFIED"

  # BR-HABIT-SKIP-004: Prompt interativo CLI
  Scenario: Interactive prompt with 9 options
    When the user runs "habit skip Academia" without flags
    Then the system shows prompt:
      """
      Motivo do skip:
      [1] Saúde (consulta, doença)
      [2] Trabalho (reunião, deadline)
      [3] Família (evento, emergência)
      [4] Viagem (deslocamento, fuso)
      [5] Clima (chuva, frio extremo)
      [6] Falta de Recursos (equipamento, local)
      [7] Emergência (não categorizada)
      [8] Outro motivo
      [9] Pular agora, justificar depois

      Escolha [1-9]:
      """

  Scenario: Choose option 1-8 creates SKIPPED_JUSTIFIED
    Given the user runs "habit skip Academia"
    When the user chooses option "2" (Work)
    And the user types note "Reunião urgente"
    Then the substatus is "SKIPPED_JUSTIFIED"
    And the skip_reason is "trabalho"
    And the skip_note is "Reunião urgente"

  Scenario: Choose option 9 creates SKIPPED_UNJUSTIFIED
    Given the user runs "habit skip Academia"
    When the user chooses option "9" (Justify later)
    Then the substatus is "SKIPPED_UNJUSTIFIED"
    And the skip_reason is NULL
    And the skip_note is NULL
    And the system shows the 24h deadline

  Scenario: Skip with --reason flag skips the prompt
    When the user runs "habit skip Academia --reason HEALTH"
    Then the interactive prompt is NOT shown
    And the substatus is "SKIPPED_JUSTIFIED"
    And the skip_reason is "saude"

  Scenario: Note prompt is optional
    Given the user runs "habit skip Academia"
    And the user chooses option "4" (Travel)
    When the system asks "Adicionar nota? (opcional)"
    And the user presses Enter without typing
    Then the skip_note is NULL
    And the skip_reason is "viagem"
