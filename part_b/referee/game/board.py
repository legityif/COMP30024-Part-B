# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from collections import defaultdict
from dataclasses import dataclass

from .hex import HexPos, HexDir
from .player import PlayerColor
from .actions import Action, SpawnAction, SpreadAction
from .exceptions import IllegalActionException
from .constants import *


# The CellState class is used to represent the state of a single cell on the
# game board.

@dataclass(frozen=True, slots=True)
class CellState:
    player: PlayerColor|None = None
    power: int = 0

    def __post_init__(self):
        if self.player is None or self.power > MAX_CELL_POWER:
            object.__setattr__(self, "power", 0)
            object.__setattr__(self, "player", None)

    def __str__(self):
        return f"CellState({self.player}, {self.power})"
    
    def __iter__(self):
        yield self.player
        yield self.power


@dataclass(frozen=True, slots=True)
class CellMutation:
    cell: HexPos
    prev: CellState
    next: CellState

    def __str__(self):
        return f"CellMutation({self.cell}, {self.prev}, {self.next})"


# The BoardMutation class is used to represent the *minimal* set of changes in
# the state of the board as a result of an action. 

@dataclass(frozen=True, slots=True)
class BoardMutation:
    action: Action
    cell_mutations: set[CellMutation]

    def __str__(self):
        return f"BoardMutation({self.cell_mutations})"


# The Board class encapsulates the state of the game board, and provides
# methods for applying actions to the board and querying/inspecting the state
# of the game (i.e. which player has won, if any).
#
# NOTE: This board representation is designed to be used internally by the
# referee for the purposes of validating actions and determining the result of
# the game. Don't assume this class is an "ideal" board representation for your
# own agent; you should think carefully about how to design data structures for
# representing the state of a game with respect to your chosen strategy. 

class Board:
    __slots__ = [
        "_mutable", 
        "_state", 
        "_turn_color", 
        "_history"
    ]

    def __init__(self, initial_state: dict[HexPos, CellState]={}):
        self._state: dict[HexPos, CellState] = \
            defaultdict(lambda: CellState(None, 0))
        self._state.update(initial_state)
        self._turn_color: PlayerColor = PlayerColor.RED
        self._history: list[BoardMutation] = []

    def __getitem__(self, cell: HexPos) -> CellState:
        """
        Return the state of a cell on the board.
        """
        if not self._within_bounds(cell):
            raise IndexError(f"Cell position '{cell}' is invalid.")
        return self._state[cell]

    def apply_action(self, action: Action):
        """
        Apply an action to a board, mutating the board state. Throws an
        IllegalActionException if the action is invalid.
        """
        match action:
            case SpawnAction():
                res_action = self._resolve_spawn_action(action)
            case SpreadAction():
                res_action = self._resolve_spread_action(action)
            case _:
                raise IllegalActionException(
                    f"Unknown action {action}", self._turn_color)

        for mutation in res_action.cell_mutations:
            self._state[mutation.cell] = mutation.next

        self._history.append(res_action)
        self._turn_color = self._turn_color.opponent

    def undo_action(self):
        """
        Undo the last action played, mutating the board state. Throws an
        IndexError if no actions have been played.
        """
        if len(self._history) == 0:
            raise IndexError("No actions to undo.")

        action: BoardMutation = self._history.pop()
        for mutation in action.cell_mutations:
            self._state[mutation.cell] = mutation.prev
        self._turn_color = self._turn_color.opponent

    def render(self, use_color: bool=False, use_unicode: bool=False) -> str:
        """
        Return a visualisation of the game board via a multiline string. The
        layout corresponds to the axial coordinate system as described in the
        game specification document.
        """
        def apply_ansi(str, bold=True, color=None):
            # Helper function to apply ANSI color codes
            bold_code = "\033[1m" if bold else ""
            color_code = ""
            if color == "r":
                color_code = "\033[31m"
            if color == "b":
                color_code = "\033[34m"
            return f"{bold_code}{color_code}{str}\033[0m"

        dim = BOARD_N
        output = ""
        for row in range(dim * 2 - 1):
            output += "    " * abs((dim - 1) - row)
            for col in range(dim - abs(row - (dim - 1))):
                # Map row, col to r, q
                r = max((dim - 1) - row, 0) + col
                q = max(row - (dim - 1), 0) + col
                if self._cell_occupied(HexPos(r, q)):
                    color, power = self._state[HexPos(r, q)]
                    color = "r" if color == PlayerColor.RED else "b"
                    text = f"{color}{power}".center(4)
                    if use_color:
                        output += apply_ansi(text, color=color, bold=False)
                    else:
                        output += text
                else:
                    output += " .. "
                output += "    "
            output += "\n"
        return output
    
    @property
    def turn_count(self) -> int:
        """
        The number of actions that have been played so far.
        """
        return len(self._history)

    @property
    def turn_color(self) -> PlayerColor:
        """
        The player (color) whose turn it is.
        """
        return self._turn_color
    
    @property
    def game_over(self) -> bool:
        """
        True iff the game is over.
        """
        if self.turn_count < 2: 
            return False
        
        return any([
            self.turn_count >= MAX_TURNS,
            self._color_power(PlayerColor.RED) == 0,
            self._color_power(PlayerColor.BLUE) == 0
        ])
    
    @property
    def winner_color(self) -> PlayerColor | None:
        """
        The player (color) who won the game, or None if no player has won.
        """
        if not self.game_over:
            return None
        
        red_power = self._color_power(PlayerColor.RED)
        blue_power = self._color_power(PlayerColor.BLUE)

        if abs(red_power - blue_power) < WIN_POWER_DIFF:
            return None
        
        return (PlayerColor.RED, PlayerColor.BLUE)[red_power < blue_power]
    
    @property
    def _total_power(self) -> int:
        """
        The total power of all cells on the board.
        """
        return sum(map(lambda cell: cell.power, self._state.values()))
    
    def _player_cells(self, color: PlayerColor) -> list[CellState]:
        return list(filter(
            lambda cell: cell.player == color,
            self._state.values()
        ))

    def _color_power(self, color: PlayerColor) -> int:
        return sum(map(lambda cell: cell.power, self._player_cells(color)))
    
    def _within_bounds(self, coord: HexPos) -> bool:
        r, q = coord
        return 0 <= r < BOARD_N and 0 <= q < BOARD_N
    
    def _cell_occupied(self, coord: HexPos) -> bool:
        return self._state[coord].power > 0

    def _validate_action_pos_input(self, pos: HexPos):
        if type(pos) != HexPos or not self._within_bounds(pos):
            raise IllegalActionException(
                f"'{pos}' is not a valid position.", self._turn_color)

    def _validate_action_dir_input(self, dir: HexDir):
        if type(dir) != HexDir:
            raise IllegalActionException(
                f"'{dir}' is not a valid direction.", self._turn_color)

    def _validate_spawn_action_input(self, action: SpawnAction):
        if type(action) != SpawnAction:
            raise IllegalActionException(
                f"Action '{action}' is not a SPAWN action.", self._turn_color)

        self._validate_action_pos_input(action.cell)

    def _validate_spread_action_input(self, action: SpreadAction):
        if type(action) != SpreadAction:
            raise IllegalActionException(
                f"Action '{action}' is not a SPREAD action.", self._turn_color)

        self._validate_action_pos_input(action.cell)
        self._validate_action_dir_input(action.direction)

    def _resolve_spawn_action(self, action: SpawnAction) -> BoardMutation:
        self._validate_spawn_action_input(action)

        cell = action.cell

        if (self._total_power >= MAX_TOTAL_POWER):
            raise IllegalActionException(
                f"Total board power max reached ({MAX_TOTAL_POWER})", 
                self._turn_color)

        if self._cell_occupied(cell):
            raise IllegalActionException(
                f"Cell {cell} is occupied.", self._turn_color)

        return BoardMutation(
            action,
            cell_mutations={CellMutation(cell, self._state[cell], 
                                         CellState(self._turn_color, 1)
            )},
        )

    def _resolve_spread_action(self, action: SpreadAction) -> BoardMutation:
        self._validate_spread_action_input(action)

        from_cell, dir = action.cell, action.direction
        action_player: PlayerColor = self._turn_color

        if self[from_cell].player != action_player:
            raise IllegalActionException(
                f"SPREAD cell {from_cell} not occupied by {action_player}",
                self._turn_color)

        # Compute destination cell coords.
        to_cells = [
            from_cell + dir * (i + 1) for i in range(self[from_cell].power)
        ]

        return BoardMutation(
            action,
            cell_mutations={
                # Remove token stack from source cell.
                CellMutation(from_cell, self[from_cell], CellState()),
            } | {
                # Add token stack to destination cells.
                CellMutation(to_cell, self[to_cell], 
                    CellState(action_player, self[to_cell].power + 1)
                ) for to_cell in to_cells
            }
        )
