from dataclasses import dataclass, field
from chess.entities.move import Move


@dataclass
class MoveCommand(Move):
    elapsed: int = field(default=0)
    from_token: object = field(default=None)
    checkpoints: list = field(default_factory=list)  # [(due_time, row, col), ...]
    current_row: int = field(default=None)
    current_col: int = field(default=None)

    def __post_init__(self):
        if self.current_row is None:
            self.current_row = self.from_row
        if self.current_col is None:
            self.current_col = self.from_col
