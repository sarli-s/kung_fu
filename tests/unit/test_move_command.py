from chess.entities.move_command import MoveCommand


def test_inherits_move_fields_and_elapsed_default():
    mc = MoveCommand(0, 0, 1, 1)
    assert mc.from_row == 0
    assert mc.to_row == 1
    assert mc.elapsed == 0


def test_elapsed_mutation():
    mc = MoveCommand(0, 0, 1, 1)
    mc.elapsed += 5
    assert mc.elapsed == 5
