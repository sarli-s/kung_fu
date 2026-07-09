from abc import ABC, abstractmethod
from chess.config import EMPTY_CELL


class TokenFormat(ABC):
    @abstractmethod
    def encode(self, token: str): pass

    @abstractmethod
    def decode(self, value) -> str: pass

    @abstractmethod
    def empty(self): pass

    @abstractmethod
    def color(self, value) -> str: pass

    @abstractmethod
    def piece_type(self, value) -> str: pass


class TextTokenFormat(TokenFormat):
    def encode(self, token: str) -> str:
        return token

    def decode(self, value) -> str:
        return value

    def empty(self) -> str:
        return EMPTY_CELL

    def color(self, value) -> str:
        return value[0]

    def piece_type(self, value) -> str:
        return value[1]


class BinaryTokenFormat(TokenFormat):
    def encode(self, token: str) -> bytes:
        return token.encode("utf-8")

    def decode(self, value) -> str:
        return value.decode("utf-8")

    def empty(self) -> bytes:
        return EMPTY_CELL.encode("utf-8")

    def color(self, value) -> str:
        return chr(value[0])

    def piece_type(self, value) -> str:
        return chr(value[1])
