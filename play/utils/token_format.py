from abc import ABC, abstractmethod
from play.config import EMPTY_CELL


class TokenFormat(ABC):
    @abstractmethod
    def encode(self, token: str):
        """Convert a canonical text token (e.g. 'wK', '.') to internal storage format."""

    @abstractmethod
    def decode(self, value) -> str:
        """Convert an internal storage value back to a canonical text token."""

    @abstractmethod
    def empty(self):
        """Returns the encoded representation of an empty cell."""

    @abstractmethod
    def color(self, value) -> str:
        """Extracts color ('w'/'b') from an encoded token."""

    @abstractmethod
    def piece_type(self, value) -> str:
        """Extracts piece type ('K','Q','R',...) from an encoded token."""


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
