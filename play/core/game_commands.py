from dataclasses import dataclass, field
from play.entities.move import Move


@dataclass
class MoveCommand(Move):
    elapsed: int = field(default=0)


@dataclass
class JumpCommand:
    row: int
    col: int
    remaining: int
