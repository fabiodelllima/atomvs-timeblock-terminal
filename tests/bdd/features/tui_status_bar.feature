# language: en
Feature: TUI Status Bar (BR-TUI-007)
  As a TimeBlock user
  I want a persistent status bar at the bottom
  So that I always see routine, timer and time context

  # R01: Posição fixa no rodapé
  Scenario: Status bar is always visible at the bottom
    Given the TUI application is running
    Then the status bar should be visible
    And the status bar should be docked at the bottom

  # R02: Seção esquerda mostra rotina ativa
  Scenario: Status bar shows active routine name
    Given the active routine is "Rotina Matinal"
    Then the status bar left section should show "Rotina Matinal"

  # R07: Sem rotina ativa mostra placeholder
  Scenario: Status bar shows placeholder when no routine is active
    Given no routine is active
    Then the status bar left section should show "[Sem rotina]"

  # R03: Seção central mostra timer ativo
  Scenario: Status bar shows active timer info
    Given a timer is running for "Academia"
    And the elapsed time is "00:45:30"
    Then the status bar center section should show "Academia"
    And the status bar center section should show "00:45:30"

  Scenario: Status bar shows no timer when idle
    Given no timer is active
    Then the status bar center section should be empty or hidden

  # R04: Seção direita mostra hora atual
  Scenario: Status bar shows current time
    Given the current time is "14:30"
    Then the status bar right section should show "14:30"

  # R05: Hora atualiza a cada minuto
  Scenario: Clock updates every minute
    Given the TUI application is running
    Then the status bar clock should use a 60-second update interval

  # R06: Timer atualiza a cada segundo quando ativo
  Scenario: Timer display updates every second when active
    Given a timer is running for "Academia"
    Then the status bar timer should use a 1-second update interval
