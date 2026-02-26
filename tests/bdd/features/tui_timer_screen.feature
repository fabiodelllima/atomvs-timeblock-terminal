# language: en
Feature: TUI Timer Screen Live Display (BR-TUI-006)
  As a TimeBlock user
  I want a live timer display in the TUI
  So that I can track time with real-time feedback

  # R01: Display atualiza a cada 1 segundo
  Scenario: Timer display shows elapsed time updating every second
    Given the TUI Timer screen is active
    And a timer is running for "Academia"
    Then the elapsed time display should update every 1 second

  # R02: Keybindings de timer
  Scenario: Start timer with 's' keybinding
    Given the TUI Timer screen is active
    And no timer is currently running
    When the user presses 's'
    Then a timer should start

  Scenario: Pause and resume with 'p' keybinding
    Given the TUI Timer screen is active
    And a timer is running
    When the user presses 'p'
    Then the timer should be paused

    When the user presses 'p' again
    Then the timer should resume

  Scenario: Stop timer with 'enter' keybinding
    Given the TUI Timer screen is active
    And a timer is running
    When the user presses 'enter'
    Then the timer should stop
    And the session summary should be displayed

  Scenario: Cancel timer with 'c' keybinding
    Given the TUI Timer screen is active
    And a timer is running
    When the user presses 'c'
    Then a confirmation dialog should appear

  # R03: Display mostra informações do timer
  Scenario: Display shows habit name and status
    Given a timer is running for "Academia"
    Then the display should show "Academia"
    And the display should show status "RUNNING"

  Scenario: Display shows paused state
    Given a timer is paused for "Academia"
    Then the display should show status "PAUSED"

  # R04: Pause congela display
  Scenario: Paused timer freezes elapsed display
    Given a timer is paused for "Academia"
    Then the elapsed time display should not update

  # R05: Stop exibe resumo
  Scenario: Stop shows session summary with duration
    Given a timer was running for "Academia" for 90 minutes
    When the timer is stopped
    Then the summary should show total duration
    And the summary should show completion percentage

  # R07: Timer ativo visível na status bar
  Scenario: Active timer updates status bar from any screen
    Given a timer is running for "Academia"
    When the user navigates to Dashboard screen
    Then the status bar should show "Academia" timer info
