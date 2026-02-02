"""Test to verify CI blocks broken code."""


def test_intentional_failure():
    """This test should fail and block CI."""
    assert False, "CI must block this!"
