# language: en
Feature: TUI Visual Consistency (BR-TUI-008)
  As a TimeBlock TUI user
  I want a consistent Material-like visual design
  So that the interface is professional and easy to scan

  # BR-TUI-008-R01: Paleta definida em theme.tcss (SSOT)

  Scenario: Theme file defines color palette
    Given the TUI theme file exists
    Then it defines a background color
    And it defines a primary accent color
    And it defines status colors for success, warning and error

  # BR-TUI-008-R02: Cards com estilo consistente

  Scenario: Cards have border, padding and margin
    Given a Card widget is rendered
    Then the card has a visible border
    And the card has padding of 1 vertical and 2 horizontal
    And the card has margin of 1

  Scenario: Cards display title in bold
    Given a Card widget with title "Hábitos Hoje"
    Then the title is rendered in bold

  # BR-TUI-008-R03: Cores de status

  Scenario: Done status uses success color
    Given a status indicator with value "done"
    Then the indicator uses the success color

  Scenario: Pending status uses warning color
    Given a status indicator with value "pending"
    Then the indicator uses the warning color

  Scenario: Missed status uses error color
    Given a status indicator with value "missed"
    Then the indicator uses the error color

  # BR-TUI-008-R04: Hierarquia tipográfica

  Scenario: Screen titles use bold weight
    Given a screen title "Dashboard"
    Then the title is rendered in bold

  Scenario: Metadata uses dim style
    Given a metadata label "14:30 - 15:00"
    Then the label is rendered in dim style

  # BR-TUI-008-R05: NavBar com largura consistente

  Scenario: NavBar spans full width at bottom
    Given the TUI is open
    Then the NavBar is docked at the bottom
    And the NavBar height is 1 row
