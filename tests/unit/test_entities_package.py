def test_package_imports():
    from chess.entities import board, move, move_command, jump

    assert hasattr(board, "Board")
    assert hasattr(move, "Move")
    assert hasattr(move_command, "MoveCommand")
    assert hasattr(jump, "JumpCommand")
