# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from dataclasses import dataclass
from enum import Enum
from typing import Generator

from .constants import BOARD_N


# HexVec represents a vector in the axial coordinate system used by the game.
# Operator overloading is used to conveniently add/subtract/multiply vectors.
# e.g. HexVec(1, 2) + HexVec(3, 4) == HexVec(4, 6)
#
# NOTE: For the purposes of the game, we usually work with HexPos objects,
# which are just HexVecs with additional bounds checking. HexVec instances are
# used for intermediate calculations, e.g. multiplying a HexDir by an integer
# to get a HexVec ("offset"), then adding that to a HexPos to get a new HexPos.

@dataclass(frozen=True, slots=True)
class HexVec:
    r: int
    q: int

    def __add__(self, other: 'HexVec') -> 'HexVec':
        return self.__class__(self.r + other.r, self.q + other.q)

    def __sub__(self, other: 'HexVec') -> 'HexVec':
        return self.__class__(self.r - other.r, self.q - other.q)

    def __neg__(self) -> 'HexVec':
        return self.__class__(self.r * -1, self.q * -1)

    def __mul__(self, n: int) -> 'HexVec':
        return self.__class__(self.r * n, self.q * n)

    def __iter__(self) -> Generator[int, None, None]:
        yield self.r
        yield self.q


# HexDir represents a direction in the axial coordinate system used by the
# game. Most importantly, it's used to represent the direction of a spread
# action (see actions.py), and can be added to a HexPos to get the position of
# neighbouring cells.

class HexDir(Enum):

    DownRight = HexVec(0, 1)
    Down      = HexVec(-1, 1)
    DownLeft  = HexVec(-1, 0)
    UpLeft    = HexVec(0, -1)
    Up        = HexVec(1, -1)
    UpRight   = HexVec(1, 0)

    @classmethod
    def _missing_(cls, value: tuple[int, int]):
        for item in cls:
            if item.value == HexVec(*value):
                return item
        raise ValueError(f"Invalid hex direction: {value}")

    def __neg__(self) -> 'HexDir':
        return HexDir(-self.value)

    def __mul__(self, n: int) -> 'HexVec':
        return self.value * n

    def __str__(self) -> str:
        return {
            HexDir.DownRight: "[↘]",
            HexDir.Down:      "[↓]",
            HexDir.DownLeft:  "[↙]",
            HexDir.UpLeft:    "[↖]",
            HexDir.Up:        "[↑]",
            HexDir.UpRight:   "[↗]"
        }[self]

    def __getattribute__(self, __name: str) -> int:
        match __name:
            case "r":
                return self.value.r
            case "q":
                return self.value.q
            case _:
                return super().__getattribute__(__name)


# HexPos represents a position in the axial coordinate system used by the game.
# Similar to HexDir, it's used to represent the position of a cell on the board
# in Action dataclasses (see actions.py). For convenience and safety, it also
# ensures computed vector additions/subtractions are within the bounds of the
# board, and throws an exception if trying to create an out-of-bounds position.

@dataclass(order=True, frozen=True)
class HexPos(HexVec):

    def __post_init__(self):
        if not (0 <= self.r < BOARD_N) or not (0 <= self.q < BOARD_N):
            raise ValueError(f"Out-of-bounds board position: {self}")

    def __str__(self):
        return f"{self.r}-{self.q}"

    def __add__(self, other: 'HexDir|HexVec') -> 'HexPos':
        return self.__class__(
            (self.r + other.r) % BOARD_N, 
            (self.q + other.q) % BOARD_N,
        )

    def __sub__(self, other: 'HexDir|HexVec') -> 'HexPos':
        return self.__class__(
            (self.r - other.r) % BOARD_N, 
            (self.q - other.q) % BOARD_N
        )
