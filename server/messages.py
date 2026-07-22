from dataclasses import dataclass, field, asdict


def to_json_dict(msg) -> dict:
    return asdict(msg)


# --- piece states ---

@dataclass(frozen=True)
class PieceStateSimple:
    state: str  # "airborne" | "short_rest" | "long_rest"


@dataclass(frozen=True)
class PieceStateMoving:
    state: str  # "moving"
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    elapsed: float
    checkpoints: tuple


# --- outgoing server messages ---

@dataclass(frozen=True)
class BoardStateMessage:
    type: str
    room_id: str
    board: tuple
    states: dict
    moves: dict
    players: dict
    game_over: bool
    scores: dict
    elapsed_ms: float


@dataclass(frozen=True)
class LoginOkMessage:
    type: str
    username: str
    color: str


@dataclass(frozen=True)
class LoginErrorMessage:
    type: str
    reason: str


@dataclass(frozen=True)
class MoveResponseMessage:
    type: str
    success: bool
    reason: str
    notation: str


@dataclass(frozen=True)
class JumpResponseMessage:
    type: str
    success: bool
    reason: str
    notation: str


@dataclass(frozen=True)
class ErrorMessage:
    type: str
    success: bool
    reason: str
