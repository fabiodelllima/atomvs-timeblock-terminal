"""Testes para fixtures de workflow."""


def test_complete_routine_setup(complete_routine_setup):
    """Testa setup completo de rotina com hábitos e instâncias."""
    routine = complete_routine_setup["routine"]
    habits = complete_routine_setup["habits"]
    instances = complete_routine_setup["instances"]

    assert routine.id is not None
    assert len(habits) == 2
    assert len(instances) > 0

    for habit in habits:
        assert habit.routine_id == routine.id

    for instance in instances:
        assert instance.habit_id in [h.id for h in habits]
