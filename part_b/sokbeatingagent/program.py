# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7
MINIMAX_DEPTH = 3
OPENING_GAME = 15
EARLY_GAME = 30
MID_GAME = 50
LATE_GAME = 70
MOVE_TIME_LIMIT = 6
MAX_TIME_LIMIT = 150

import random, math
import time
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
DIRECTIONS = (HexDir.Up, HexDir.UpLeft, HexDir.UpRight, HexDir.Down, HexDir.DownLeft, HexDir.DownRight)

class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size
        self.count = size
        
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            if self.rank[root_x] < self.rank[root_y]:
                root_x, root_y = root_y, root_x
            self.parent[root_y] = root_x
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_x] += 1
            self.count -= 1
            
    def get_count(self):
        return self.count

class boardState:
    def __init__(self, turn, board=None):
        if board is None:
            self._board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        else:
            boardcopy = [row[:] for row in board]
            self._board = boardcopy
        self._turn = turn
    
    def validTotalBoardPower(self):
        power = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self._board[i][j] is not None:
                    power += self._board[i][j][1]
        return power<49
    
    def reachedTerminal(self):
        player, enemy = 0, 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self._board[r][c] is not None:
                    if self._board[r][c][0]==PlayerColor.BLUE:
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
        self._total_time = 0
        if color==PlayerColor.RED:
            self._enemy = PlayerColor.BLUE
        else:
            self._enemy = PlayerColor.RED
        self._turn = 0
        self._state = boardState(self._turn, None)
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
        self._turn += 1 
        return self.best_move(self._state, self._color)
    
    def minimax(self, state, depth, max_depth, player, alpha, beta):
        if state.reachedTerminal() or depth==max_depth:
            if (self._turn <= OPENING_GAME):
                return self.opening_game(state)
            elif (OPENING_GAME <= self._turn < EARLY_GAME): 
                return self.early_game(state)
            elif (EARLY_GAME <= self._turn < MID_GAME):
                return self.mid_game(state)
            else:
                return self.late_game(state)
        is_maximising = (player == self._color)
        best_score = -1e8 if is_maximising else 1e8
        moves = self.generate_moves(player, state)
        for move in moves:
            new_state = self.applyMovetoBoard(state, move, player)
            score = self.minimax(new_state, depth+1, max_depth, self._enemy if player == self._color else self._color, alpha, beta)
            if is_maximising:
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if alpha>=beta:
                    return best_score
            else:
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if alpha>=beta:
                    return best_score
        return best_score

    def best_move(self, state, player):
        start_time = time.time()
        best_score = -1e8
        best_moves = []
        moves = self.generate_ordered_moves(player, state)
        for move in moves:
            # shouldn't happen often
            if self._total_time > MAX_TIME_LIMIT:
                return self.greedymove(state, player, moves)
            if time.time() - start_time > MOVE_TIME_LIMIT:
                self._total_time += time.time() - start_time
                return random.choice(best_moves)
            new_state = self.applyMovetoBoard(state, move, player)
            # if big difference in score, return fast greedy move
            if self.num_cell_diff(new_state)>=10 or self.total_power_diff(new_state)>=12:
                self._total_time += time.time() - start_time
                return self.greedymove(state, player, moves)
            # otherwise do minimax
            score = self.minimax(new_state, 1, MINIMAX_DEPTH, self._enemy, -1e8, 1e8)
            # print(str(move), score)
            if score > best_score:  # update best_score
                best_score = score
                best_moves = [move]  # reset best_moves
            elif score == best_score:  # append to best_moves
                best_moves.append(move)
        if len(best_moves) == 0:
            self._total_time += time.time() - start_time
            return self.greedymove(state, player, moves)
        else:
            self._total_time += time.time() - start_time
            return random.choice(best_moves)
    
    def greedymove(self, state, player, moves):
        best_moves = []
        max_heuristic = -1e8
        for move in moves:
            new_state = self.applyMovetoBoard(state, move, player)
            if self.total_power_diff(new_state)>max_heuristic:
                best_moves = [move]
                max_heuristic = self.total_power_diff(new_state)
            elif self.total_power_diff(new_state)==max_heuristic:
                best_moves.append(move)
        return best_moves[0] if len(best_moves)==1 else random.choice(best_moves)  
    
    # STUFF TO DO WITH EVALUATION FUNCTIONS
    def opening_game(self, state):
        if (self.get_power(state, self._color)==0):
            return -1e7
        if (self.get_power(state, self._enemy)==0):
            return 1e7
        player_connectivity = self.count_connected_components(state, self._color)
        enemy_connectivity = self.count_connected_components(state, self._enemy)
        connectivity_diff = enemy_connectivity - player_connectivity
        num_cell_diff = self.num_cell_diff(state)
        total_power_diff = self.total_power_diff(state)
        safety = self.safety(state)
        return 0.4*total_power_diff + 0.4*num_cell_diff + 0.1*connectivity_diff + 0.05*safety
    
    def early_game(self, state):
        if (self.get_power(state, self._color)==0):
            return -1e7
        if (self.get_power(state, self._enemy)==0):
            return 1e7
        player_connectivity = self.count_connected_components(state, self._color)
        enemy_connectivity = self.count_connected_components(state, self._enemy)
        connectivity_diff = enemy_connectivity - player_connectivity
        num_cell_diff = self.num_cell_diff(state)
        total_power_diff = self.total_power_diff(state)
        safety = self.safety(state)
        return 0.5*total_power_diff + 0.35*num_cell_diff + 0.1*connectivity_diff + 0.05*safety

    def mid_game(self, state):
        if (self.get_power(state, self._color)==0):
            return -1e7
        if (self.get_power(state, self._enemy)==0):
            return 1e7
        total_power_diff = self.total_power_diff(state)
        num_cell_diff = self.num_cell_diff(state)
        return 0.7*total_power_diff + 0.3*num_cell_diff
    
    def late_game(self, state):
        if (self.get_power(state, self._color)==0):
            return -1e7
        if (self.get_power(state, self._enemy)==0):
            return 1e7
        total_power_diff = self.total_power_diff(state)
        num_cell_diff = self.num_cell_diff(state)
        return 0.95*total_power_diff + 0.05*num_cell_diff
    
    def num_cell_diff(self, state):
        # consider player power compared to enemy power after a move
        player_cells, enemy_cells = 0, 0
        board = state._board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0] == self._color:
                        player_cells += 1
                    else:
                        enemy_cells += 1
        # consider how many moves you can make compared to enemy
        return player_cells - enemy_cells
    
    def safety(self, state):
        safety = 0
        board = state._board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0] == self._color:
                        for d in DIRECTIONS:
                            new_r, new_c = HexPos(r, c) + d
                            if board[new_r][new_c] is not None:
                                if board[new_r][new_c][0] == self._color:
                                    safety += 1
                                elif board[new_r][new_c][0] == self._enemy:
                                    safety -=1
        return safety
    
    def generate_spawns(self, player, state):
        board = state._board
        # Use a set to store the enemy cells
        enemy_cells = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None and board[r][c][0] != player:
                    enemy_cells.add((HexPos(r, c), board[r][c][1]))
        # Use a list comprehension or filter to generate valid_spawns
        valid_spawns = [HexPos(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) 
                        if board[r][c] is None and 
                        not any(self.dist(HexPos(r, c), enemy_cell[0]) <= enemy_cell[1] for enemy_cell in enemy_cells)]
        spawn_moves = [SpawnAction(pos) for pos in valid_spawns]
        return spawn_moves
    
    def dist(self, cell1, cell2):
        board_size = BOARD_SIZE
        dx = abs(cell1.q - cell2.q)
        dy = abs(cell1.r - cell2.r)
        if dx > board_size / 2:
            dx = board_size - dx
        if dy > board_size / 2:
            dy = board_size - dy
        d = math.sqrt(dx ** 2 + dy ** 2)
        return board_size - d if dx == 0 or dy == 0 or dx == dy else d
    
    def get_power(self, state, player):
        # consider player power compared to enemy power after a move
        player_power = 0
        board = state._board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0] == player:
                        player_power += board[r][c][1]
        # consider how many moves you can make compared to enemy
        return player_power
    
    def total_power_diff(self, state):
        # consider player power compared to enemy power after a move
        player_power, enemy_power = 0, 0
        board = state._board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0] == self._color:
                        player_power += board[r][c][1]
                    else:
                        enemy_power += board[r][c][1]
        # consider how many moves you can make compared to enemy
        return player_power - enemy_power
    
    def generate_ordered_moves(self, player, state):
        possible_moves = []
        validBoard = state.validTotalBoardPower()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if validBoard and state._board[i][j] is None and state._turn!=343:
                    possible_moves.append(SpawnAction(HexPos(i, j))) 
                else:
                    if state._board[i][j] is not None and state._board[i][j][0]==player and state._turn!=343:
                        for d in DIRECTIONS:
                            possible_moves.append(SpreadAction(HexPos(i, j), d))
                    else:
                        continue 
        # Evaluate moves and sort list
        if (self._turn < OPENING_GAME):
            moves_with_eval = [(move, self.opening_game(self.applyMovetoBoard(state, move, player))) for move in possible_moves]
        elif (OPENING_GAME <= self._turn < EARLY_GAME):
            moves_with_eval = [(move, self.early_game(self.applyMovetoBoard(state, move, player))) for move in possible_moves]
        elif (EARLY_GAME <= self._turn < MID_GAME):
            moves_with_eval = [(move, self.mid_game(self.applyMovetoBoard(state, move, player))) for move in possible_moves]
        else:
            moves_with_eval = [(move, self.late_game(self.applyMovetoBoard(state, move, player))) for move in possible_moves]
        moves_with_eval.sort(key = lambda x: x[1], reverse=True)
        # Return ordered list of moves
        return [move for move, _ in moves_with_eval]
        
    def applyMovetoBoard(self, state, action, maximising_player):
        new_state = boardState(self._turn, state._board)
        new_board = new_state._board
        match action:
            case SpawnAction(cell):
                # for both agent colours, add to board 
                if PlayerColor.RED == maximising_player:
                    new_board[cell.r][cell.q] = (maximising_player, 1)
                if PlayerColor.BLUE == maximising_player:
                    new_board[cell.r][cell.q] = (maximising_player, 1)
                return new_state
            case SpreadAction(cell, direction):
                orig_cell = cell
                if PlayerColor.RED == maximising_player:
                    # call spread to update board
                    self.spreadInDir(new_board, direction, cell, orig_cell, new_board[cell.r][cell.q][1], maximising_player)
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
    
    # def count_connected_components(self, state, player):
    #     board = state._board
    #     visited = set()
    #     count = 0
    #     for r in range(len(board)):
    #         for c in range(len(board[0])):
    #             if (r, c) not in visited and board[r][c] is not None and board[r][c][0]==player:
    #                 count += 1
    #                 queue = [(r, c)]
    #                 visited.add((r, c))
    #                 while queue:
    #                     row, col = queue.pop(0)
    #                     for dr, dc in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
    #                         new_r, new_c = row + dr, col + dc
    #                         if 0 <= new_r < len(board) and 0 <= new_c < len(board[0]) and (new_r, new_c) not in visited and board[new_r][new_c] is not None and board[new_r][new_c][0] == board[r][c][0]:
    #                             queue.append((new_r, new_c))
    #                             visited.add((new_r, new_c))
    #     return count
    
    def count_connected_components(self, state, player):
        board = state._board
        size = len(board) * len(board[0])
        uf = UnionFind(size)
        for r in range(len(board)):
            for c in range(len(board[0])):
                if board[r][c] is not None and board[r][c][0] == player:
                    pos = r * len(board[0]) + c
                    for d in DIRECTIONS:
                        new_r, new_c = HexPos(r, c) + d
                        if 0 <= new_r < len(board) and 0 <= new_c < len(board[0]) and board[new_r][new_c] is not None and board[new_r][new_c][0] == player:
                            new_pos = new_r * len(board[0]) + new_c
                            uf.union(pos, new_pos)
        return uf.get_count()
    
    def generate_moves(self, player, state):
        possible_moves = []
        validBoard = state.validTotalBoardPower()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if validBoard and state._board[i][j] is None and state._turn!=343:
                    possible_moves.append(SpawnAction(HexPos(i, j))) 
                else:
                    if state._board[i][j] is not None and state._board[i][j][0]==player and state._turn!=343:
                        for d in DIRECTIONS:
                            possible_moves.append(SpreadAction(HexPos(i, j), d))
                    else:
                        continue 
        return possible_moves