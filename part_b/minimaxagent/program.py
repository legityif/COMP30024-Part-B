# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7
MINIMAX_DEPTH = 5

from collections import deque
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
DIRECTIONS = (HexDir.Up, HexDir.UpLeft, HexDir.UpRight, HexDir.Down, HexDir.DownLeft, HexDir.DownRight)

class boardState:
    def __init__(self, color, turn, board=None):
        if board is None:
            self._board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        else:
            boardcopy = [row[:] for row in board]
            self._board = boardcopy
            pass
        self._color = color
        self._turn = turn
    
    def validTotalBoardPower(self):
        power = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self._board[i][j] is not None:
                    power += self._board[i][j][1]
        return power<49
    
    def generate_moves(self):
        if self.reachedTerminal():
            return []
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
        if (player==0 and self._turn!=0) or (enemy==0 and self._turn!=0) or (player==0 and enemy==0 and (self._turn!=0)) or self._turn==343:
            return True
        return False
        
class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        if color==PlayerColor.RED:
            self._enemy = PlayerColor.BLUE
        else:
            self._enemy = PlayerColor.RED
        self._turn = 0
        self._state = boardState(self._color, self._turn, None)
        match color:
            case PlayerColor.RED:
                print("Testing: MiniMax Agent is playing as red")
            case PlayerColor.BLUE:
                print("Testing: MiniMax Agent is playing as blue")
    
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
    
    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        match self._color:
            case PlayerColor.RED:
                self._turn += 1
                return self.best_move(self._state, self._color)
            case PlayerColor.BLUE:       
                self._turn += 1 
                return self.best_move(self._state, self._color) 
            
    
    def minimax(self, state, depth, max_depth, is_maximising, maximising_player):
        if state.reachedTerminal() or depth == max_depth:
            return self.eval_fn(state, maximising_player)
        best_score = -1e8 if is_maximising else 1e8
        moves = state.generate_moves()
        for move in moves:
            new_state = boardState(self._enemy if maximising_player == self._color else self._color, state._turn + 1, state._board)
            self.applyMovetoBoard(new_state, move, maximising_player)
            score = self.minimax(new_state, depth - 1, max_depth, not is_maximising, maximising_player)
            if is_maximising:
                best_score = max(best_score, score)
            else:
                best_score = min(best_score, score)
        return best_score
    
    def best_move(self, state, maximising_player):
        best_score = -1e8 if maximising_player==self._color else 1e8
        best_move = None
        moves = state.generate_moves()
        for move in moves:
            new_state = boardState(self._color, state._turn + 1, state._board)  
            self.applyMovetoBoard(new_state, move, maximising_player)
            if maximising_player==self._color:
                score = self.minimax(new_state, MINIMAX_DEPTH, MINIMAX_DEPTH, True, self._color)
            else:
                score = self.minimax(new_state, MINIMAX_DEPTH, MINIMAX_DEPTH, False, self._enemy)
            if self._color == maximising_player:
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
        return best_move
    
    def eval_fn(self, state, maximising_player):
        score = 0
        board = state._board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0]==self._color:
                        if self._color == maximising_player:
                            score += (board[r][c][1] + self.heuristic_infinite_spread(board, maximising_player))
                        else:
                            score -= (board[r][c][1] + self.heuristic_infinite_spread(board, maximising_player))
                    else:
                        if self._color == maximising_player:
                            score += (board[r][c][1] + self.heuristic_infinite_spread(board, maximising_player))
                        else:
                            score -= (board[r][c][1] + self.heuristic_infinite_spread(board, maximising_player))          
        return score
    
    def applyMovetoBoard(self, state, action, maximising_player):
        new_state = boardState(maximising_player, self._turn, state._board.copy())
        new_board = new_state._board
        match action:
            case SpawnAction(cell):
                # for both agent colours, add to board 
                if PlayerColor.RED == maximising_player:
                    new_board[cell.r][cell.q] = (maximising_player, 1)
                    return new_state
                if PlayerColor.BLUE == maximising_player:
                    new_board[cell.r][cell.q] = (maximising_player, 1)
                    return new_state
            case SpreadAction(cell, direction):
                orig_cell = cell
                if PlayerColor.RED == maximising_player:
                    # call spread to update board
                    self.spreadInDir(new_board, direction, cell, orig_cell, new_board[cell.r][cell.q][1], maximising_player)
                    return new_state
                if PlayerColor.BLUE == maximising_player:
                    # call spread to update board
                    self.spreadInDir(new_board, direction, cell, orig_cell, new_board[cell.r][cell.q][1], maximising_player)
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

    def heuristic_infinite_spread(self, board, maximising_player):
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
                    if board[r][c][0]==maximising_player:
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