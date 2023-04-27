# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from enum import Enum
from abc import abstractmethod
from .actions import Action


# PlayerColor is an enum used by the referee to identify the two players on the
# game board as per the game rules ("red" and "blue"). The referee will pass
# this to your agent when it is initialised in order to tell it which player it
# should be playing as, and is also used to distinguish between the two players
# in the turn() method (i.e. whose action has been played).

class PlayerColor(Enum):
    RED = 0
    BLUE = 1

    def __str__(self) -> str:
        """
        String representation of a player colour identifier.
        """
        return {
            PlayerColor.RED: "RED",
            PlayerColor.BLUE: "BLUE"
        }[self]

    def __index__(self) -> int:
        """
        Return the index of the player (0 or 1).
        """
        return self.value

    def __int__(self) -> int:
        """
        Player value in zero-sum form (+1 RED, -1 BLUE). 
        """
        return 1 - 2 * self.value

    @property
    def opponent(self) -> "PlayerColor":
        """
        Return the other player colour (there are only two!).
        """
        match self:
            case PlayerColor.RED:
                return PlayerColor.BLUE
            case PlayerColor.BLUE:
                return PlayerColor.RED


# Player is an abstract base class for actual players of the game -- it's used
# internally by the referee to wrap your agent and/or other virtual players.

class Player:
    def __init__(self, color: PlayerColor):
        self._color = color

    @property
    def color(self) -> PlayerColor:
        return self._color

    def __str__(self) -> str:
        return str(self._color)

    @abstractmethod
    async def action(self) -> Action:
        """
        Get the next action for the player.
        """
        raise NotImplementedError

    @abstractmethod
    async def turn(self, color: PlayerColor, action: Action):
        """
        Notify the player that an action has been played.
        """
        raise NotImplementedError

    async def __aenter__(self) -> 'Player':
        """
        Context manager: Any resource allocation should be done here.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager: Any resource cleanup should be done here.
        """
        pass
