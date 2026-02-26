# language: en
# BR-VAL-002: Validação de Datas
Feature: Date Validation (BR-VAL-002)
  As a system
  I need to validate dates
  So that only valid dates within acceptable range are processed

  Background:
    Given the system is configured with minimum date as 2025-01-01

  Scenario: Accept minimum valid date
    Given I have a date "2025-01-01"
    When I validate the date
    Then the date should be accepted
    And the returned date should be 2025-01-01

  Scenario: Accept date after minimum
    Given I have a date "2025-06-15"
    When I validate the date
    Then the date should be accepted
    And the returned date should be 2025-06-15

  Scenario: Reject date before minimum
    Given I have a date "2024-12-31"
    When I validate the date
    Then the validation should fail with message "Date cannot be before 2025-01-01"

  Scenario: Reject date far before minimum
    Given I have a date "2020-01-01"
    When I validate the date
    Then the validation should fail with message "Date cannot be before 2025-01-01"

  Scenario: Accept future dates without limit
    Given I have a date "2030-12-31"
    When I validate the date
    Then the date should be accepted
    And the returned date should be 2030-12-31

  Scenario: Accept far future date
    Given I have a date "2050-01-01"
    When I validate the date
    Then the date should be accepted
    And the returned date should be 2050-01-01

  Scenario: Accept date in ISO 8601 format with string
    Given I have a date string "2025-03-15"
    When I validate the date
    Then the date should be accepted
    And the returned date should be 2025-03-15

  Scenario: Reject invalid ISO 8601 format
    Given I have a date string "15/03/2025"
    When I validate the date
    Then the validation should fail with message "Date must be in ISO 8601 format (YYYY-MM-DD)"

  Scenario: Reject invalid date format with dots
    Given I have a date string "2025.03.15"
    When I validate the date
    Then the validation should fail with message "Date must be in ISO 8601 format (YYYY-MM-DD)"

  Scenario: Reject empty date string
    Given I have an empty date string
    When I validate the date
    Then the validation should fail with message "Date cannot be empty"

  Scenario: Reject invalid date values
    Given I have a date string "2025-13-01"
    When I validate the date
    Then the validation should fail with message "Invalid date"

  Scenario: Reject impossible date
    Given I have a date string "2025-02-30"
    When I validate the date
    Then the validation should fail with message "Invalid date"
