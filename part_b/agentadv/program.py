# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7
MINIMAX_DEPTH = 2
LATE_GAME = 50

import random, math
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
        self._color = color
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
        self._has_safe_spawns = True
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
            
    def minimax(self, state, depth, max_depth, player, alpha, beta):
        if state.reachedTerminal() or depth==max_depth:
            return self.adv_eval_fn(state)
        is_maximising = (player == self._color)
        best_score = -1e8 if is_maximising else 1e8
        moves = self.generate_ordered_moves(player, state)
        for move in moves:
            new_state = self.applyMovetoBoard(state, move, player)
            score = self.minimax(new_state, depth+1, max_depth, self._enemy if player == self._color else self._color, alpha, beta)
            if is_maximising:
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if alpha>=beta:
                    break
            else:
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta<=alpha:
                    break
        return best_score
    
    def best_move(self, state, player):
        best_score = -1e8
        best_moves = []
        moves = self.generate_moves(player, state)
        for move in moves:
            new_state = self.applyMovetoBoard(state, move, player)
            score = self.minimax(new_state, 1, MINIMAX_DEPTH, self._enemy, -1e8, 1e8)
            if score > best_score:  # update best_score
                best_score = score
                best_moves = [move]  # reset best_moves
            elif score == best_score:  # append to best_moves
                best_moves.append(move)
        if len(best_moves) == 0:
            print("error no best move")
            return None
        else:
            best_move = best_moves[0] if len(best_moves)==1 else random.choice(best_moves)   
            return best_move
    
    def power_eval_fn(self, state):
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
    
    def hybrid_eval_fn(self, state):
        # consider player power compared to enemy power after a move
        player_power, enemy_power = 0, 0
        player_cells, enemy_cells = 0, 0
        board = state._board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0] == self._color:
                        player_power += board[r][c][1]
                        player_cells += 1
                    else:
                        enemy_power += board[r][c][1]
                        enemy_cells += 1
        # consider how many moves you can make compared to enemy
        return player_power - enemy_power + 2*(player_cells - enemy_cells)
    
    def adv_eval_fn(self, state):
        # consider player power compared to enemy power after a move
        player_power, enemy_power = 0, 0
        player_cells, enemy_cells = 0, 0
        board = state._board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0] == self._color:
                        player_power += board[r][c][1]
                        player_cells += 1
                    else:
                        enemy_power += board[r][c][1]
                        enemy_cells += 1
        # consider how many moves you can make compared to enemy
        # if no more safe moves?
        player_safe_spawns = len(self.generate_spawns(self._color, state))
        enemy_safe_spawns = len(self.generate_spawns(self._enemy, state))
        if player_safe_spawns==0:
            return player_power - enemy_power + 2*(player_cells - enemy_cells)
        else:
            spawn_mobility_diff = player_safe_spawns-enemy_safe_spawns
            return 0.9*(player_power - enemy_power) + 0.1*(spawn_mobility_diff)
    
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
        moves_with_eval = [(move, self.adv_eval_fn(self.applyMovetoBoard(state, move, player))) for move in possible_moves]
        moves_with_eval.sort(key=lambda x: x[1], reverse=True)
        # Return ordered list of moves
        return [move for move, _ in moves_with_eval]
        
    def applyMovetoBoard(self, state, action, maximising_player):
        new_state = boardState(maximising_player, self._turn, state._board)
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
    
    # def minimax(self, state, depth, max_depth, player, alpha, beta, tt):
    #     # Check if we've already evaluated this state
    #     tt_entry = tt.get(state)
    #     if tt_entry is not None and tt_entry['depth'] >= depth:
    #         if tt_entry['flag'] == 'exact':
    #             return tt_entry['score']
    #         elif tt_entry['flag'] == 'lowerbound':
    #             alpha = max(alpha, tt_entry['score'])
    #         elif tt_entry['flag'] == 'upperbound':
    #             beta = min(beta, tt_entry['score'])
    #         if alpha >= beta:
    #             return tt_entry['score']

    #     if state.reachedTerminal() or depth==max_depth:
    #         score = self.hybrid_eval_fn(state)
    #         # Store the evaluation in the transposition table
    #         tt[state] = {'flag': 'exact', 'depth': depth, 'score': score}
    #         return score

    #     is_maximising = (player == self._color)
    #     best_score = -1e8 if is_maximising else 1e8
    #     moves = self.generate_ordered_moves(player, state)
    #     for move in moves:
    #         new_state = self.applyMovetoBoard(state, move, player)
    #         score = self.minimax(new_state, depth+1, max_depth, self._enemy if player == self._color else self._color, alpha, beta, tt)
    #         if is_maximising:
    #             best_score = max(best_score, score)
    #             alpha = max(alpha, best_score)
    #             if alpha >= beta:
    #                 break
    #         else:
    #             best_score = min(best_score, score)
    #             beta = min(beta, best_score)
    #             if alpha >= beta:
    #                 break

    #     # Store the best score in the transposition table
    #     if best_score <= alpha:
    #         flag = 'upperbound'
    #     elif best_score >= beta:
    #         flag = 'lowerbound'
    #     else:
    #         flag = 'exact'
    #     tt[state] = {'flag': flag, 'depth': depth, 'score': best_score}
    #     return best_score
    
    # def generate_ordered_moves(self, player, state):
    #     possible_moves = []
    #     validBoard = state.validTotalBoardPower()
    #     for i in range(BOARD_SIZE):
    #         for j in range(BOARD_SIZE):
    #             if validBoard and state._board[i][j] is None and state._turn!=343:
    #                 possible_moves.append(SpawnAction(HexPos(i, j))) 
    #             else:
    #                 if state._board[i][j] is not None and state._board[i][j][0]==player and state._turn!=343:
    #                     for d in DIRECTIONS:
    #                         possible_moves.append(SpreadAction(HexPos(i, j), d))
    #                 else:
    #                     continue 
    #     moves_with_eval = []
    #     for move in possible_moves:
    #         new_state = self.applyMovetoBoard(state, move, player)
    #         moves_with_eval.append([move, self.hybrid_eval_fn(new_state)])
    #     sorted_moves = sorted(moves_with_eval, key=lambda x: x[1], reverse=True)
    #     return [move[0] for move in sorted_moves]
    
        # def generate_spawns(self, player, state):
    #     board = state._board
    #     # check for spawn moves within capture zone of enemy cell
    #     valid_spawns = []
    #     enemy_cells = []
    #     for r in range(BOARD_SIZE):
    #         for c in range(BOARD_SIZE):
    #             if board[r][c] is not None:
    #                 if board[r][c][0]!=player:
    #                     enemy_cells.append((HexPos(r, c), board[r][c][1]))
    #     for r in range(BOARD_SIZE):
    #         for c in range(BOARD_SIZE):
    #             if board[r][c] is None:
    #                 pos = HexPos(r, c)
    #                 if any(self.dist(pos, enemy_cell[0]) <= enemy_cell[1] for enemy_cell in enemy_cells):
    #                     continue
    #                 valid_spawns.append(pos)
    #     spawn_moves = [SpawnAction(pos) for pos in valid_spawns]
    #     return spawn_moves