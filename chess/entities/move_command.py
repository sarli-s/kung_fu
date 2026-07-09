from dataclasses import dataclass, field
from chess.entities.move import Move


@dataclass
class MoveCommand(Move):
    elapsed: int = field(default=0)
