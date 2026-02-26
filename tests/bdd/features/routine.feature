# language: en
Feature: Routine and Context Management
  As a TimeBlock user
  I want to organize habits in routines
  So that I can switch between contexts (morning, work, night)

  # BR-ROUTINE-001: Restrição de rotina ativa única
  Scenario: Only one routine active at a time
    Given the following routines exist:
      | name            | is_active |
      | Rotina Matinal  | true      |
      | Rotina Trabalho | false     |
      | Rotina Noite    | false     |
    When the system validates the constraint
    Then only 1 routine has is_active = true

  Scenario: Activating a routine deactivates all others
    Given "Rotina Matinal" is active
    When the user runs "routine activate 'Rotina Trabalho'"
    Then "Rotina Trabalho" becomes active
    And "Rotina Matinal" becomes inactive
    And the system displays:
      """
      [INFO] Rotina "Rotina Matinal" desativada
      [OK] Rotina "Rotina Trabalho" ativada

      Agora a rotina ativa é: Rotina Trabalho (8 hábitos)
      """

  Scenario: Creating a routine does not activate it automatically
    When the user runs "routine create 'Rotina Fim de Semana'"
    Then the new routine is created with is_active = false
    And the previously active routine remains active

  Scenario: Deleting the active routine leaves none active
    Given "Rotina Matinal" is active
    When the user runs "routine delete 'Rotina Matinal'"
    Then the routine is deleted
    And no routine is active

  Scenario: Activation via SQL trigger/constraint
    Given the database has trigger "enforce_single_active_routine"
    When UPDATE routine SET is_active = true WHERE id = 2
    Then the trigger automatically deactivates routines with id != 2

  # BR-ROUTINE-002: Hábito pertence a rotina
  Scenario: Habit requires routine_id (NOT NULL)
    When an attempt to create a habit without routine_id is made
    Then the system returns error "routine_id obrigatório"

  Scenario: Habit created in a valid routine
    Given a routine "Rotina Matinal" with id 1 exists
    When the user creates a habit with routine_id = 1
    Then the habit is created successfully
    And the habit belongs to "Rotina Matinal"

  Scenario: Habit with invalid routine_id
    When an attempt to create a habit with routine_id = 999 is made
    Then the system returns error "Rotina não encontrada"
    And the foreign key constraint is violated

  Scenario: 1:N relationship (Routine to Habits)
    Given a routine "Rotina Matinal" exists
    When the routine contains habits:
      | title           |
      | Academia        |
      | Meditação       |
      | Café da manhã   |
    Then the routine has 3 linked habits
    And all habits have routine_id = 1

  Scenario: Delete routine with habits (cascade or block)
    Given "Rotina Matinal" contains 5 habits
    When the user runs "routine delete 'Rotina Matinal'"
    Then the system asks:
      """
      Rotina contém 5 habits.
      [1] Deletar rotina E habits (cascade)
      [2] Cancelar operação
      """

  Scenario: Delete routine with --purge removes habits
    Given "Rotina Matinal" contains 5 habits
    When the user runs "routine delete 'Rotina Matinal' --purge"
    Then the routine is deleted
    And all 5 habits are deleted

  # BR-ROUTINE-003: Task independente de rotina
  Scenario: Task does not have routine_id field
    When the Task model is inspected
    Then the field routine_id does NOT exist

  Scenario: Task created independently of active routine
    Given "Rotina Trabalho" is active
    When the user creates task "Dentista (25/11 14:30)"
    Then the task is created without routine_id
    And the task does not depend on the active routine

  Scenario: task list shows all tasks (no routine filter)
    Given "Rotina Matinal" is active
    And the following tasks exist:
      | title             |
      | Dentista          |
      | Reunião cliente   |
    When the user runs "task list"
    Then the system shows all 2 tasks
    And does not filter by active routine

  Scenario: Switching routines does not affect tasks
    Given tasks "Dentista" and "Reunião cliente" exist
    And "Rotina Matinal" is active
    When the user runs "routine activate 'Rotina Trabalho'"
    And the user runs "task list"
    Then the same 2 tasks are displayed

  Scenario: Deleting routine does not affect tasks
    Given 3 tasks have been created
    And "Rotina Matinal" is deleted
    When the user runs "task list"
    Then all 3 tasks remain

  Scenario: Task vs Habit (differences)
    Then the differences are:
      | aspect       | Task           | Habit                 |
      | Recurrence   | One-time       | Recurring             |
      | Routine      | Not linked     | Required              |
      | Context      | Independent    | Depends on routine    |
      | Example      | Dentist 14:30  | Gym 07:00-08:30       |

  # BR-ROUTINE-004: Cascade de ativação
  Scenario: habit list shows only habits from the active routine
    Given "Rotina Matinal" is active with habits:
      | title       |
      | Academia    |
      | Meditação   |
    And "Rotina Trabalho" is inactive with habits:
      | title          |
      | Daily Standup  |
      | Deep Work      |
    When the user runs "habit list"
    Then the system shows only:
      | title       |
      | Academia    |
      | Meditação   |

  Scenario: habit create uses active routine automatically
    Given "Rotina Matinal" is active (id = 1)
    When the user runs "habit create --title 'Leitura'"
    Then the habit is created with routine_id = 1
    And the system displays:
      """
      ✓ Hábito criado na rotina ativa: Rotina Matinal
      """

  Scenario: Switching routine changes habit list context
    Given "Rotina Matinal" is active
    When the user runs "habit list"
    Then it shows habits from "Rotina Matinal"

    When the user runs "routine activate 'Rotina Trabalho'"
    And the user runs "habit list"
    Then it shows habits from "Rotina Trabalho"

  Scenario: Error when no routine is active
    Given all routines are inactive
    When the user runs "habit list"
    Then the system returns error:
      """
      [ERROR] Nenhuma rotina ativa.

      Para ativar uma rotina:
        routine list
        routine activate <id>
      """

  Scenario: Flag --all-routines escapes context
    Given "Rotina Matinal" is active
    When the user runs "habit list --all-routines"
    Then the system shows habits from ALL routines:
      | title          | routine         |
      | Academia       | Matinal         |
      | Meditação      | Matinal         |
      | Daily Standup  | Trabalho        |
      | Deep Work      | Trabalho        |

  Scenario: Flag --routine specifies a different routine
    Given "Rotina Matinal" is active
    When the user runs "habit create --routine 2 --title 'Teste'"
    Then the habit is created in routine id = 2
    And does not use the active routine

  Scenario: Commands independent of active routine
    Given "Rotina Matinal" is active
    Then independent commands are:
      | command         | behavior                     |
      | routine list    | Shows ALL routines           |
      | task list       | Shows ALL tasks              |
      | report habit 42 | Accepts habit_id (no filter) |

  Scenario: Routine context in CLI prompt
    Given "Rotina Matinal" is active
    When the user opens the CLI
    Then the prompt shows:
      """
      TimeBlock [Rotina Matinal] >
      """

  Scenario: Activate empty routine (no habits)
    Given a routine "Rotina Fim de Semana" with no habits exists
    When the user runs "routine activate 'Rotina Fim de Semana'"
    Then the routine is activated
    And the system displays:
      """
      [OK] Rotina "Rotina Fim de Semana" ativada

      Rotina vazia. Adicione habits:
        habit create --title "Nome" --start HH:MM --end HH:MM
      """

  # BR-ROUTINE-002: Comportamentos de delete
  Scenario: Soft delete by default (is_active=False)
    Given a routine "Rotina Matinal" with 8 habits exists
    And the routine is active
    When the user runs "routine delete 1"
    And confirms the action
    Then routine.is_active = False
    And habits remain linked
    And data remains in the database
    And the system displays:
      """
      [WARN] Desativar rotina "Rotina Matinal"?
             - 8 hábitos permanecem vinculados
             - Rotina pode ser reativada depois

      Confirmar? (s/N): s
      [OK] Rotina "Rotina Matinal" desativada
      """

  Scenario: Hard delete without habits works
    Given a routine "Rotina Teste" with no habits exists
    When the user runs "routine delete 1 --purge"
    And confirms the action
    Then the routine is REMOVED from the database
    And the system displays:
      """
      [WARN] Deletar PERMANENTEMENTE rotina "Rotina Teste"?
             Esta ação NÃO pode ser desfeita.

      Confirmar? (s/N): s
      [OK] Rotina deletada permanentemente
      """

  Scenario: Hard delete with habits blocks (MVP)
    Given a routine "Rotina Matinal" with 8 habits exists
    When the user runs "routine delete 1 --purge"
    Then the system BLOCKS the delete
    And displays error message:
      """
      [ERROR] Não é possível deletar rotina com hábitos

      Rotina "Rotina Matinal" possui 8 hábitos:
      1. Academia
      2. Meditação
      ...

      Ações disponíveis:
      1. Mover hábitos para outra rotina (Sprint 2)
      2. Deletar hábitos também com --cascade (Sprint 2)

      Para deletar a rotina vazia, remova os hábitos primeiro.
      """

  # BR-ROUTINE-004: Fluxo de primeira rotina
  Scenario: Create habit without routine guides creation
    Given NO routines exist
    When the user runs "habit create --title 'Academia'"
    Then the system shows an interactive wizard:
      """
      [ERROR] Nenhuma rotina existe

      Para criar hábitos, primeiro crie uma rotina.

      Deseja criar uma rotina agora? (S/n): s

      Nome da rotina: Rotina Matinal
      [OK] Rotina "Rotina Matinal" criada e ativada

      Agora você pode criar o hábito "Academia". Continuar? (S/n): s

      [OK] Hábito "Academia" criado na rotina "Rotina Matinal"
      """

  Scenario: routine init creates default routine
    Given NO routines exist
    When the user runs "routine init"
    Then the system shows a wizard:
      """
      [INFO] Criar rotina padrão?

      Opções:
      1. Rotina Diária (recomendado para iniciantes)
      2. Criar rotina personalizada

      Escolha (1/2): 1
      [OK] Rotina "Minha Rotina Diária" criada e ativada

      Próximo passo: habit create --title "Seu Primeiro Hábito"
      """

  Scenario: First routine created is activated automatically
    Given NO routines exist
    When the user creates the first routine "Rotina Matinal"
    Then routine.is_active = True AUTOMATICALLY
    And the system displays:
      """
      [OK] Rotina "Rotina Matinal" criada e ativada automaticamente

      Como esta é sua primeira rotina, ela já está ativa.
      """
