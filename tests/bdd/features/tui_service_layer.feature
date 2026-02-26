# language: en
Feature: TUI Service Layer Sharing (BR-TUI-009)
  As a TimeBlock TUI
  I want to share the same services as the CLI
  So that no business logic is duplicated

  # R01: TUI usa mesmos services que CLI
  Scenario: TUI imports services from timeblock.services
    Given the TUI session helper exists
    Then it should provide a database session
    And the session should be compatible with all services

  # R02: TUI nunca acessa models diretamente
  Scenario: TUI accesses data only through services
    Given the TUI service layer is configured
    Then RoutineService should be accessible
    And HabitService should be accessible
    And TaskService should be accessible
    And TimerService should be accessible

  # R03: Session per action
  Scenario: Each operation gets its own session
    Given the TUI session helper exists
    When two operations are executed sequentially
    Then each should use an independent session

  # R04: Erros propagados como notificação
  Scenario: Service errors propagate to TUI
    Given a service raises ValueError
    Then the error message should be available to the TUI

  # R05: Commit automático em sucesso, rollback em erro
  Scenario: Successful operation commits
    Given a session is opened via the helper
    When the operation succeeds
    Then the session should be committed

  Scenario: Failed operation rolls back
    Given a session is opened via the helper
    When the operation raises an exception
    Then the session should be rolled back
