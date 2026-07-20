"""
Command protocol and move validation.
"""


def coords_to_notation(row, col):
    """Convert (row, col) board coordinates to chess square notation (e.g. (6,4) -> 'e2')."""
    return chr(ord('a') + col) + str(8 - row)


class MoveValidator:
    """Validates and executes move commands on a GameEngine."""

    def __init__(self, engine):
        self.engine = engine

    def parse_chess_notation(self, notation):
        if not notation or len(notation) != 4:
            return None, None, None, None
        
        from_col_char = notation[0]
        from_row_char = notation[1]
        to_col_char = notation[2]
        to_row_char = notation[3]
        
        if not (from_col_char in "abcdefgh" and to_col_char in "abcdefgh"):
            return None, None, None, None
        if not (from_row_char in "12345678" and to_row_char in "12345678"):
            return None, None, None, None
        
        from_col = ord(from_col_char) - ord('a')
        from_row = 8 - int(from_row_char)
        to_col = ord(to_col_char) - ord('a')
        to_row = 8 - int(to_row_char)
        
        return from_row, from_col, to_row, to_col

    def execute_move(self, notation):
        from_row, from_col, to_row, to_col = self.parse_chess_notation(notation)
        
        if from_row is None:
            return False, "Invalid notation format (expected e2e4)"
        
        was_moving = self.engine.is_moving(from_row, from_col)
        self.engine.request_move(from_row, from_col, to_row, to_col)
        # Infer success via state transition — avoids reimplementing engine legality logic
        is_moving_now = self.engine.is_moving(from_row, from_col)
        if not was_moving and is_moving_now:
            return True, "Move executed"
        else:
            return False, "Move rejected by engine"


class JumpValidator:
    """Validates and executes jump commands on a GameEngine."""

    def __init__(self, engine):
        self.engine = engine

    def parse_chess_notation(self, notation):
        if not notation or len(notation) != 2:
            return None, None
        
        col_char = notation[0]
        row_char = notation[1]
        
        if not (col_char in "abcdefgh" and row_char in "12345678"):
            return None, None
        
        col = ord(col_char) - ord('a')
        row = 8 - int(row_char)
        
        return row, col

    def execute_jump(self, notation):
        row, col = self.parse_chess_notation(notation)
        
        if row is None:
            return False, "Invalid notation format (expected e2)"
        
        was_airborne = self.engine.is_airborne(row, col)
        self.engine.request_jump(row, col)
        # Infer success via state transition — avoids reimplementing engine legality logic
        is_airborne_now = self.engine.is_airborne(row, col)
        if not was_airborne and is_airborne_now:
            return True, "Jump executed"
        else:
            return False, "Jump rejected by engine"
