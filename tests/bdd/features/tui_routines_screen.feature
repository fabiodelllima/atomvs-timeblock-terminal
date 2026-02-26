# language: en
Feature: TUI Routines Screen (BR-TUI-011)
  As a TimeBlock TUI user
  I want to view my week in a temporal grid layout
  So that I can plan and adjust my recurring habits

  # BR-TUI-011-R01: Header com lista de rotinas

  Scenario: Header displays routines with active indicator
    Given the TUI is on the Routines screen
    And the following routines exist:
      | name            | active |
      | Rotina Matinal  | yes    |
      | Rotina Trabalho | no     |
    Then the header shows "Rotina Matinal" and "Rotina Trabalho"
    And "Rotina Matinal" has an active indicator

  Scenario: Empty routine shows guidance message
    Given the TUI is on the Routines screen
    And the active routine has no habits
    Then the grid shows "No habits. Press [n]"

  # BR-TUI-011-R02: Grade semanal 7 colunas

  Scenario: Grid displays 7 day columns
    Given the TUI is on the Routines screen
    And the active routine has habits
    Then the grid shows columns from Monday to Sunday
    And the vertical ruler shows hours from 06:00 to 22:00

  # BR-TUI-011-R03: Blocos proporcionais na grade

  Scenario: One-hour habit occupies 2 rows in the grid
    Given a habit "Academia" from 07:00 to 08:00 exists
    When the grid is rendered
    Then the "Academia" block occupies 2 rows

  Scenario: Thirty-minute habit occupies 1 row in the grid
    Given a habit "Meditação" from 06:00 to 06:30 exists
    When the grid is rendered
    Then the "Meditação" block occupies 1 row

  # BR-TUI-011-R04: Navegação na grade

  Scenario: Arrow keys navigate between days and blocks
    Given the TUI is on the Routines screen
    And the active routine has habits
    When I press right arrow
    Then the focus moves to the next day
    When I press down arrow
    Then the focus moves to the next block

  Scenario: Brackets navigate between weeks
    Given the TUI is on the Routines screen
    When I press "]"
    Then the grid advances one week
    When I press "["
    Then the grid goes back one week

  # BR-TUI-011-R05: Painel de detalhes

  Scenario: Selecting a habit shows the detail panel
    Given the TUI is on the Routines screen
    And a habit "Academia" exists in the grid
    When I select the "Academia" block
    Then the side panel shows name "Academia"
    And the panel shows schedule, duration and recurrence

  # BR-TUI-011-R07: Ativação de rotina

  Scenario: Pressing 'a' activates the selected routine
    Given the TUI is on the Routines screen
    And the focus is on the header
    And "Rotina Trabalho" is selected
    When I press "a"
    Then "Rotina Trabalho" becomes active
    And the grid reloads with habits from "Rotina Trabalho"

  # BR-TUI-011-R08: Conflitos exibidos lado a lado

  Scenario: Overlapping habits show error border
    Given the TUI is on the Routines screen
    And overlapping habits exist:
      | name     | start | end   |
      | Academia | 07:00 | 08:00 |
      | Corrida  | 07:30 | 08:30 |
    When the grid is rendered
    Then the conflicting blocks are displayed side by side
    And both have an error border

  # BR-TUI-011-R12: Navegação cross-screen

  Scenario: Pressing 'g' navigates to Habits with filter
    Given the TUI is on the Routines screen
    And the "Academia" block is selected
    When I press "g"
    Then the TUI navigates to the Habits screen
    And the filter is applied for "Academia"
