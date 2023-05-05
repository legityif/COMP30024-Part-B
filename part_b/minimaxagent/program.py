# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
DIRECTIONS = (HexDir.Up, HexDir.UpLeft, HexDir.UpRight, HexDir.Down, HexDir.DownLeft, HexDir.DownRight)

class boardState:
    def __init__(self, board):
        self.board = board
        
class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        self._turn = 0
        self._state = boardState([[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)])
        match color:
            case PlayerColor.RED:
                print("Testing: RandomAgent is playing as red")
            case PlayerColor.BLUE:
                print("Testing: RandomAgent is playing as blue")
                
    def minimax(self, state, depth, maximizing_player):
        if depth==0:
            return self.evaluatestate(state)
        if maximizing_player:
            curr_max = float('-inf')
            for move in self.generate_moves(state):
                pass
        else:
            pass
            
        
    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        bestScore = -1e8
        bestMove = None
        match self._color:
            case PlayerColor.RED:
                pass
            case PlayerColor.BLUE:                
                pass
        self._turn += 1
        return bestMove

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                if PlayerColor.RED == color:
                    self._state.board[cell.r][cell.q] = (color, 1)
                    pass
                if PlayerColor.BLUE == color:
                    self._state.board[cell.r][cell.q] = (color, 1)
                    pass
            case SpreadAction(cell, direction):
                orig_cell = cell
                if PlayerColor.RED == color:
                    self.spreadInDir(self._state.board, direction, cell, orig_cell, self._state.board[cell.r][cell.q][1], color)
                    pass
                if PlayerColor.BLUE == color:
                    self.spreadInDir(self._board, direction, cell, orig_cell, self._state.board[cell.r][cell.q][1], color)
                    pass
    
    def applyMovetoBoard(self, state, action, color):
        board = [row[:] for row in state.board]
        state = state(board)
        match action:
            case SpawnAction(cell):
                # for both agent colours, add to board 
                if PlayerColor.RED == color:
                    board[cell.r][cell.q] = (color, 1)
                    return state
                if PlayerColor.BLUE == color:
                    board[cell.r][cell.q] = (color, 1)
                    return state
            case SpreadAction(cell, direction):
                orig_cell = cell
                if PlayerColor.RED == color:
                    # call spread to update board
                    self.spreadInDir(board, direction, cell, orig_cell, board[cell.r][cell.q][1], color)
                    return state
                if PlayerColor.BLUE == color:
                    # call spread to update board
                    self.spreadInDir(board, direction, cell, orig_cell, board[cell.r][cell.q][1], color)
                    return state
    
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
                if self._state.board[i][j] is not None:
                    power += self._state.board[i][j][1]
        return power<49
    
    def generate_moves(self, state):
        possible_moves = []
        curr_board = state.board
        validBoard = self.validTotalBoardPower()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if validBoard and curr_board[i][j] is None:
                    possible_moves.append(SpawnAction(HexPos(i, j))) 
                else:
                    if curr_board[i][j] is not None and curr_board[i][j][0] == self._color:
                        for d in DIRECTIONS:
                            possible_moves.append(SpreadAction(HexPos(i, j), d))
                    else:
                        continue 
        return possible_moves

    def reachedTerminal(self, state):
        player, enemy = 0, 0
        board = state.board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0]==self._color:
                        player += board[r][c][1]
                    else:
                        enemy += board[r][c][1]
        if player==0 or enemy==0 or (player==0 and enemy==0) or self._turn==343:
            return True
        return False

    def eval_terminal_state(self, state):
        pass
    
