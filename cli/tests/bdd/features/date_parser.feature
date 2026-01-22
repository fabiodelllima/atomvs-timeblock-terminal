# language: en
Feature: Date Parser CLI (BR-CLI-002)
  As a CLI user
  I want to input dates in multiple formats
  So that I have flexibility in data entry

  Background:
    Given the system is initialized

  Scenario: Accept ISO 8601 format
    When I provide the date "2025-06-15"
    Then the parsed date should be 2025-06-15

  Scenario: Accept day-first format with dash
    When I provide the date "15-06-2025"
    Then the parsed date should be 2025-06-15

  Scenario: Accept day-first format with slash
    When I provide the date "15/06/2025"
    Then the parsed date should be 2025-06-15

  Scenario: Reject date before minimum
    When I provide the date "31-12-2024"
    Then it should raise error "Date cannot be before 2025-01-01"

  Scenario: Reject invalid calendar date
    When I provide the date "30/02/2025"
    Then it should raise error "Invalid date"

  Scenario: Accept valid leap day
    When I provide the date "29/02/2028"
    Then the parsed date should be 2028-02-29

  Scenario: Accept date object passthrough
    When I provide a date object for 2025-06-15
    Then the parsed date should be 2025-06-15

  Scenario: Reject empty string input
    When I provide an empty date string
    Then it should raise error "Date cannot be empty"
