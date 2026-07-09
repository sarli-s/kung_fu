from dataclasses import dataclass


@dataclass
class JumpCommand:
    row: int
    col: int
    remaining: int
