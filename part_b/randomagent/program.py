# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir


# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!

class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        self._board = []
        # self._board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        match color:
            case PlayerColor.RED:
                print("Testing: RandomAgent is playing as red")
            case PlayerColor.BLUE:
                print("Testing: RandomAgent is playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        match self._color:
            case PlayerColor.RED:
                # get all possible moves based on current board 
                # use a random function to get a random move based on board 
                # return this move
                self.generate_moves(self._board)
                return SpawnAction(HexPos(1, 1))
                # return SpreadAction(HexPos(3, 3), HexDir.Up)
            case PlayerColor.BLUE:
                # get all possible moves based on current board 
                # use a random function to get a random move based on board 
                # return this move
                self.generate_moves(self._board)
                return SpawnAction(HexPos(1, 1))
                # return SpreadAction(HexPos(3, 3), HexDir.Up)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                # for both agent colours, add to board 
                if PlayerColor.RED == color:
                    self._board.append((color, action, cell))
                    pass
                if PlayerColor.BLUE == color:
                    self._board.append((color, action, cell))
                    pass
            case SpreadAction(cell, direction):
                # for both agent colours, add to board 
                if PlayerColor.RED == color:
                    self._board.append((color, action, cell))
                    pass
                if PlayerColor.BLUE == color:
                    self._board.append((color, action, cell))
                    pass

    def generate_moves(self, _board):
        print([(col, action, pos) for col, action, pos in _board] if len(self._board)!=0 else "NO MYPLAYER MOVES YET")
        for col, action, pos in self._board:
            if PlayerColor == col:
                pass
                

    