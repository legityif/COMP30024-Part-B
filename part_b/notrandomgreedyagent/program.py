# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7
from collections import deque

import random
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
DIRECTIONS = (HexDir.Up, HexDir.UpLeft, HexDir.UpRight, HexDir.Down, HexDir.DownLeft, HexDir.DownRight)

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
        self._board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        match color:
            case PlayerColor.RED:
                print("Testing: Greedy is playing as red")
            case PlayerColor.BLUE:
                print("Testing: Greedy is playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        match self._color:
            case PlayerColor.RED:
                best_move = None
                max_heuristic = -1e8
                possible_moves = self.generate_moves()
                for move in possible_moves:
                    actionedBoard = self.applyMovetoBoard(self._board, move, self._color)
                    if self.heuristic(actionedBoard)>max_heuristic:
                        best_move = move
                        max_heuristic = self.heuristic(actionedBoard)
                return best_move

            case PlayerColor.BLUE:
                best_moves = []
                max_heuristic = -1e8
                possible_moves = self.generate_moves()
                for move in possible_moves:
                    actionedBoard = self.applyMovetoBoard(self._board, move, self._color)
                    if self.heuristic(actionedBoard)>max_heuristic:
                        best_moves = [move]
                        max_heuristic = self.heuristic(actionedBoard)
                    elif self.heuristic(actionedBoard)==max_heuristic:
                        best_moves.append(move)
                return best_moves[0] if len(best_moves)==1 else random.choice(best_moves)   

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
                orig_cell = cell
                if PlayerColor.RED == color:
                    # call spread to update board
                    self.spreadInDir(self._board, direction, cell, orig_cell, self._board[cell.r][cell.q][1], color)
                    pass
                if PlayerColor.BLUE == color:
                    # call spread to update board
                    self.spreadInDir(self._board, direction, cell, orig_cell, self._board[cell.r][cell.q][1], color)
                    pass
    
    def applyMovetoBoard(self, orig_board, action, color):
        board = [row[:] for row in orig_board]
        match action:
            case SpawnAction(cell):
                # for both agent colours, add to board 
                if PlayerColor.RED == color:
                    board[cell.r][cell.q] = (color, 1)
                    return board
                if PlayerColor.BLUE == color:
                    board[cell.r][cell.q] = (color, 1)
                    return board
            case SpreadAction(cell, direction):
                orig_cell = cell
                if PlayerColor.RED == color:
                    # call spread to update board
                    self.spreadInDir(board, direction, cell, orig_cell, board[cell.r][cell.q][1], color)
                    return board
                if PlayerColor.BLUE == color:
                    # call spread to update board
                    self.spreadInDir(board, direction, cell, orig_cell, board[cell.r][cell.q][1], color)
                    return board
    
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

    def heuristic(self, board):
        your_power, their_power = 0, 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0]==self._color:
                        your_power += board[r][c][1]
                    else:
                        their_power += board[r][c][1]
        return your_power - their_power
                
    def heuristic_infinite_spread(self, board):
        """
        Since a red cell has to be one the same "line" as a blue cell (where a line is the straight line connecting the red and blue cell)
        in order to take over the blue cell, we can find the minimum number of lines that it takes to connect all the blue cells. 
        Where two blue cells are considered to be on the same "line" if they are connected in a straight line, in either the x, y, or z direction.
        """

        # first put all the blue cells into a queue
        queue = deque()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c]:
                    if board[r][c][0]==self._color:
                        queue.append((r, c))
        
        # Keep track of the marked row, column, and diagonals
        visited = {"r0": False, "r1": False, "r2": False, "r3": False, "r4": False, "r5": False, "r6": False,
                "c0": False, "c1": False, "c2": False, "c3": False, "c4": False, "c5": False, "c6": False,
                "d0": False, "d1": False, "d2": False, "d3": False, "d4": False, "d5": False, "d6": False}
        totalExpanded = 0
        
        while(queue):
            r, c = queue.popleft()
            # check if this cell has already been marked on the corresponding row, col, or diagonal
            # sum of 7 --> diagonal 0, sum of 10 --> diagonal 3, sum of 11 --> diagonal 4, sum of 12 --> diagonal 5
            # if r+c = n, where n < 7, then n is the diagonal number, otherwise, modulo it with 7   
            row = "r" + str(r)
            col = "c" + str(c)
            diag = "d" + str((r+c)%BOARD_SIZE)

            if visited[row]==True or visited[col]==True or visited[diag]==True:
                continue
            else:
                # this cell is not on a marked line, we need to spread it in all 3 directions (mark all lines as visited)
                visited[row] = True
                visited[col] = True
                visited[diag] = True
                totalExpanded += 1
        return totalExpanded
                
                
class boardState:
    def __init__(self, board):
        self.board = board
    
    