from chess.entities.jump import JumpCommand


def test_jump_fields_and_remaining():
    j = JumpCommand(2, 3, 5)
    assert j.row == 2
    assert j.col == 3
    assert j.remaining == 5
    # simulate decrement if caller reduces remaining
    j.remaining -= 1
    assert j.remaining == 4
