# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from dataclasses import dataclass

from .hex import HexPos, HexDir


# Here we define dataclasses for the two possible actions that a player can
# make. See the `hex.py` file for the definition of the `HexPos` and `HexDir`.
# If you are unfamiliar with dataclasses, see the relevant Python docs here:
# https://docs.python.org/3/library/dataclasses.html 


@dataclass(frozen=True, slots=True)
class SpawnAction():
    cell: HexPos

    def __str__(self) -> str:
        return f"SPAWN({self.cell.r}, {self.cell.q})"


@dataclass(frozen=True, slots=True)
class SpreadAction():
    cell: HexPos
    direction: HexDir

    def __str__(self) -> str:
        return f"SPREAD({self.cell.r}, {self.cell.q}, " + \
               f"{self.direction.r}, {self.direction.q})"


Action = SpawnAction | SpreadAction
