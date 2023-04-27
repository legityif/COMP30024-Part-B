# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7

import random
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
        # self._board = []
        self._board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
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
                possible_moves = self.generate_moves()
                return self.randomMove(possible_moves)
            case PlayerColor.BLUE:
                possible_moves = self.generate_moves()
                return self.randomMove(possible_moves)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                # for both agent colours, add to board 
                if PlayerColor.RED == color:
                    self._board[cell.r][cell.q] = (color, 1)
                    pass
                if PlayerColor.BLUE == color:
                    self._board[cell.r][cell.q] = (color, 1)
                    pass
            case SpreadAction(cell, direction):
                # for both agent colours, add to board 
                if PlayerColor.RED == color:
                    self._board[cell.r][cell.q] = (color, 1)
                    pass
                if PlayerColor.BLUE == color:
                    self._board[cell.r][cell.q] = (color, 1)
                    pass
                
    def randomMove(self, possible_moves):
        rand_move = random.randint(0, len(possible_moves))
        return possible_moves[rand_move]

    def generate_moves(self):
        print("\n")
        print(self._board)
        print("\n")
        possible_moves = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self._board[i][j] is None:
                    possible_moves.append(SpawnAction(HexPos(i, j)))
                else:
                    if self._board[i][j][0] == self._color:
                        possible_moves.append(SpreadAction(HexPos(i, j), HexDir.Up))
                        possible_moves.append(SpreadAction(HexPos(i, j), HexDir.UpLeft))
                        possible_moves.append(SpreadAction(HexPos(i, j), HexDir.UpRight))
                        possible_moves.append(SpreadAction(HexPos(i, j), HexDir.Down))
                        possible_moves.append(SpreadAction(HexPos(i, j), HexDir.DownRight))
                        possible_moves.append(SpreadAction(HexPos(i, j), HexDir.DownLeft))
                    else:
                        continue 
        return possible_moves
                

    