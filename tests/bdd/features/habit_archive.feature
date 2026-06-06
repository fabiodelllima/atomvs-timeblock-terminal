# language: en
Feature: Habit Archive Lifecycle
  As a ATOMVS user
  I want deleting a habit to archive it instead of destroying history
  So that streaks and adherence data are preserved and the action is reversible

  # BR-HABIT-005: Deleção com semântica de archive
  # BR-HABIT-006: Archive Lifecycle (archive / purge / restore)
  # ADR-057: Archive Lifecycle para Habit

  Scenario: Archive preserves history
    Given a habit with 30 days of TimeLog history
    When I delete the habit
    Then the habit is marked as archived
    And all 30 TimeLog entries remain intact
    And the streak calculation for the past period remains correct

  Scenario: Archived habit excluded from listing
    Given an archived habit
    When I list habits
    Then the archived habit is not shown
    When I list habits with --all flag
    Then the archived habit appears with archive timestamp

  Scenario: Purge requires explicit confirmation
    Given an archived habit with associated instances and timelogs
    When I run "habit purge" command
    Then I am prompted to type the word "purge" literally
    When I type "y" instead of "purge"
    Then the operation is aborted
    And no data is destroyed
