# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7

import random
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
DIRECTIONS = (HexDir.Up, HexDir.UpLeft, HexDir.UpRight, HexDir.Down, HexDir.DownLeft, HexDir.DownRight)

class boardState:
    def __init__(self, color, board=None):
        if board is None:
            self._board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        else:
            boardcopy = [row[:] for row in board]
            self._board = boardcopy
            pass
        self._color = color
    
    def validTotalBoardPower(self):
        power = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self._board[i][j] is not None:
                    power += self._board[i][j][1]
        return power<49
    
    def generate_moves(self):
        possible_moves = []
        validBoard = self.validTotalBoardPower()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if validBoard and self._board[i][j] is None:
                    possible_moves.append(SpawnAction(HexPos(i, j))) 
                else:
                    if self._board[i][j] is not None and self._board[i][j][0] == self._color:
                        for d in DIRECTIONS:
                            possible_moves.append(SpreadAction(HexPos(i, j), d))
                    else:
                        continue 
        return possible_moves
    
    def reachedTerminal(self):
        player, enemy = 0, 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self._board[r][c] is not None:
                    if self._board[r][c][0]==self._color:
                        player += self._board[r][c][1]
                    else:
                        enemy += self._board[r][c][1]
        if player==0 or enemy==0 or (player==0 and enemy==0) or self._turn==343:
            return True
        return False
        
class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        self._turn = 0
        self._state = boardState(self._color, None)
        match color:
            case PlayerColor.RED:
                print("Testing: RandomAgent is playing as red")
            case PlayerColor.BLUE:
                print("Testing: RandomAgent is playing as blue")
    
    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                if PlayerColor.RED == color:
                    self._state._board[cell.r][cell.q] = (color, 1)
                    pass
                if PlayerColor.BLUE == color:
                    self._state._board[cell.r][cell.q] = (color, 1)
                    pass
            case SpreadAction(cell, direction):
                orig_cell = cell
                if PlayerColor.RED == color:
                    self.spreadInDir(self._state._board, direction, cell, orig_cell, self._state._board[cell.r][cell.q][1], color)
                    pass
                if PlayerColor.BLUE == color:
                    self.spreadInDir(self._state._board, direction, cell, orig_cell, self._state._board[cell.r][cell.q][1], color)
                    pass
    
    def randomMove(self, possible_moves):
        rand_move = random.randint(0, len(possible_moves)-1)
        return possible_moves[rand_move]
    
    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        match self._color:
            case PlayerColor.RED:
                possible_moves = self._state.generate_moves()
                self._turn += 1
                return self.randomMove(possible_moves)
            case PlayerColor.BLUE:                
                possible_moves = self._state.generate_moves()
                self._turn += 1
                return self.randomMove(possible_moves)
    
    def applyMovetoBoard(self, state, action, color):
        new_state = boardState(state.board, color)
        new_board = new_state.board
        match action:
            case SpawnAction(cell):
                # for both agent colours, add to board 
                if PlayerColor.RED == color:
                    new_board[cell.r][cell.q] = (color, 1)
                    return new_state
                if PlayerColor.BLUE == color:
                    new_board[cell.r][cell.q] = (color, 1)
                    return new_state
            case SpreadAction(cell, direction):
                orig_cell = cell
                if PlayerColor.RED == color:
                    # call spread to update board
                    self.spreadInDir(new_board, direction, cell, orig_cell, new_board[cell.r][cell.q][1], color)
                    return new_state
                if PlayerColor.BLUE == color:
                    # call spread to update board
                    self.spreadInDir(new_board, direction, cell, orig_cell, new_board[cell.r][cell.q][1], color)
                    return new_state
    
    def spreadInDir(self, board, direction, cell, orig_cell, power, colour):
        while power>0:
            new_cell = HexPos(cell.r, cell.q) + direction
            if board[new_cell.r][new_cell.q]==None:
                board[new_cell.r][new_cell.q] = (colour, 1)
            else:
                if board[new_cell.r][new_cell.q][1]+1 > 6:
                    board[new_cell.r][new_cell.q] = None
                else:
                    board[new_cell.r][new_cell.q] = (colour, board[new_cell.r][new_cell.q][1]+1)
            cell = new_cell
            power-=1
        board[orig_cell.r][orig_cell.q] = None
        cell = orig_cell
