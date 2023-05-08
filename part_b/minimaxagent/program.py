# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
import random, math, time
from collections import deque

# Define agent constants and game settings
DIRS = [HexDir.DownRight, HexDir.Down, HexDir.DownLeft, HexDir.UpLeft, HexDir.Up, HexDir.UpRight]
BOARD_SIZE = 7
MAX_POWER = 7
MAX_TOTAL_POWER = 49
RED = 'r'
BLUE = 'b'
MAX_COORD = 6
MIN_COORD = 0
INF = float('inf')
NEGATIVE_INF = float('-inf')
MAX_DEPTH = 3
MAX_TURNS = 343
WIN_POWER_DIFF = 2
MAX_SIM_TIME = 6
GREEDY_LIMIT = 8

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
        self._state = board_state(agent_color = self._color, board={}, move=None, turn=1, value = 0, color=self._color)
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        This agent will use the minimax algorithm with alpha-beta pruning to choose 
            the move that maximizes the number of cells controlled by its own color.
        """
        global evaltime 
        evaltime = 0
        match self._color:
            case PlayerColor.RED:    
                if self._state.turn == 1:
                    return self.random()
                move = self.best_minimax_move()
            case PlayerColor.BLUE:
                move = self.best_minimax_move()
        print("eval time = " + str(evaltime))
        return move

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        self._state.turn += 1
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                if PlayerColor.RED == color:
                    self._state.board[(cell.r, cell.q)] = ("r", 1)
                else:
                    self._state.board[(cell.r, cell.q)] = ("b", 1)
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                update_board(self._state.board, cell.r, cell.q, direction)
                pass

    def best_minimax_move(self):
        # assuming there is always a move to be made
        max_value = NEGATIVE_INF
        best_moves = []
        start_time = time.time()
        # Save time and play greedy
        if count_color(self._state.board, self._color) - count_color(self._state.board, self._color.opponent) > GREEDY_LIMIT:
            return self.greedy()
        for option in generate_options(self._state, self._color, sort_moves=True):
            if time.time() - start_time > MAX_SIM_TIME:
                return random.choice(best_moves)
            value = self.minimax(state=option, depth=1, color=self._color.opponent, alpha=NEGATIVE_INF, beta=INF)
            # print(str(option.move), value)
            if value > max_value:  
                max_value = value
                best_moves = [option.move]
            elif value == max_value: 
                best_moves.append(option.move)
        if max_value == NEGATIVE_INF:
            return self.random()
        return random.choice(best_moves)

    def minimax(self, state, depth, color, alpha, beta):
        """
        Return the best move and estimated value of board state using minimax
        """
        # print(depth, state.board)
        # print(color, state.board, state.value)
        if state.game_over() and depth == 1:
            # make immediate winning moves and avoid losing moves
            if state.winner_color() == self._color:
                return INF
            else:
                return NEGATIVE_INF
        if depth == MAX_DEPTH:
            # return state.power_eval()
            # print(state.board, state.value)
            return state.value
        
        best_value = NEGATIVE_INF if color == self._color else INF
        for option in generate_options(state, color, sort_moves=True):
            value = self.minimax(option, depth + 1, color.opponent, alpha, beta)
            if color == self._color:
                # maximising
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break   
            else:
                # minimising
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if alpha >= beta:
                    break
        return best_value

    def greedy(self):
        best_moves = []
        max_value = NEGATIVE_INF
        for option in generate_options(self._state, self._color, sort_moves=True):
            val = option.greedy_eval()
            if val > max_value:
                best_moves = [option.move]
                max_value = val
            elif val == max_value:
                best_moves.append(option.move)
        return random.choice(best_moves)  

    def random(self):
        return random.choice([option.move for option in generate_options(self._state, self._color)])

class board_state:
    def __init__(self, agent_color, board, move, turn, value, color):
        self.agent_color = agent_color
        self.board = board
        self.move = move
        self.color = color
        self.value = value
        self.turn = turn
    
    def __lt__(self, other):
        return self.value < other.value
    
    def valid_state(self):
        """
        Return whether the board is a valid state
        """
        return count_power(self.board, PlayerColor.BLUE) + count_power(self.board, PlayerColor.RED) <= MAX_TOTAL_POWER

    def game_over(self):
        if self.turn < 2: 
            return False
        
        return any([
            self.turn >= MAX_TURNS,
            count_power(self.board, PlayerColor.RED) == 0,
            count_power(self.board, PlayerColor.BLUE) == 0
        ])

    def winner_color(self):
        """
        The player (color) who won the game, or None if no player has won.
        """
        if not self.game_over():
            return None
        
        red_power = count_power(self.board, PlayerColor.RED)
        blue_power = count_power(self.board, PlayerColor.BLUE)

        if abs(red_power - blue_power) < WIN_POWER_DIFF:
            return None
        
        return (PlayerColor.RED, PlayerColor.BLUE)[red_power < blue_power]
        
    def weighted_eval(self):
        '''
        Final equation for heuristic value is still to be tested and determined
        '''
        board = self.board
        color = self.agent_color
        our_power = count_power(board, color)
        opponent_power = count_power(board, color.opponent)
        num_our_cells = count_color(board, color)
        num_opponent_cells = count_color(board, color.opponent)
   
        power_w = 0.3
        cell_w = 0.4
        mobility_w = 0.1
        cc_w = 0.2
        start_time = time.time()
        # TRY IMPLEMENT DANGER LEVEL EVAL
        
        if self.turn < 15:
            player_cc =  connected_components(board, color)
            danger_level = danger(self)
            #value = 0.2*(our_power - opponent_power) + 0.45*(num_our_cells - num_opponent_cells) #+ 0.35*(our_connected_components - opponent_connected_components)
            # value = 0.2*(self.power - self.opponent_power) + 0.45*(self.num_pieces - self.num_opponent) + 0.35*(our_connected_components - opponent_connected_components) + 0.25*(self.power/self.num_pieces) - 0.1*(danger_level)
            # value = 0.2*(our_power - opponent_power) + 0.35*(num_our_cells - num_opponent_cells) + 0.55*(our_connected_components - opponent_connected_components) - 0.1*(danger_level)
            value = 0.25*(our_power - opponent_power) + 0.35*(num_our_cells - num_opponent_cells) + 0.25*player_cc - 0.1*danger_level 
            # print(color, board, value)
        elif 15 >= self.turn > 50:
            our_mobility = mobility(board, color)
            opponent_mobility = mobility(board, color.opponent)
            #value = 0.5*(our_power - opponent_power) + 0.4*(num_our_cells - num_opponent_cells) + 0.1*(our_mobility - opponent_mobility)
            value = 0.6*(our_power - opponent_power) + 0.4*(num_our_cells - num_opponent_cells)
        else:
            our_mobility = mobility(board, color)
            opponent_mobility = mobility(board, color.opponent)
            #value = 0.8*(our_power - opponent_power) + 0.1*(num_our_cells - num_opponent_cells) + 0.1*(our_mobility - opponent_mobility)
            value = 0.85*(our_power - opponent_power) + 0.15*(num_our_cells - num_opponent_cells) 
            # value = power_w*(our_power - opponent_power) + cell_w*(num_our_cells - num_opponent_cells) + mobility_w*(our_mobility - opponent_mobility) + cc_w*(our_connected_components - opponent_connected_components)
        global evaltime
        evaltime += time.time() - start_time
        return value

    def greedy_eval(self):
        board = self.board
        color = self.color
        our_power = count_power(board, color)
        opponent_power = count_power(board, color.opponent)
        num_our_cells = count_color(board, color)
        num_opponent_cells = count_color(board, color.opponent)
        return our_power + 0.5*num_our_cells - 2*num_opponent_cells
    
    def power_eval(self):
        return count_power(self.board, self.color) - count_power(self.board, self.color.opponent)

def count_power(board, color):
    '''
    Return count of colour power
    '''
    color = 'r' if color == PlayerColor.RED else 'b'
    return sum([k for player, k in board.values() if player == color])

def count_color(board, color):
    '''
    Return count of colour tokens
    '''
    color = 'r' if color == PlayerColor.RED else 'b'
    return sum([1 for player, k in board.values() if player == color])

def count_reachable_cells(board, color):
    '''
    count number of cells that can be spread to
    '''
    color = 'r' if color == PlayerColor.RED else 'b'
    count = 0
    max_power_cell = (0, 0, 0)
    for (r, q), (clr, power) in board.items():
        if clr == color and power > max_power_cell[2]:
            max_power_cell = (r, q, power)

    r, q, power = max_power_cell
    for direction in DIRS:
        rd = direction.__getattribute__("r")
        qd = direction.__getattribute__("q")
        nr = (r + rd + (power*rd)) % MAX_POWER
        nq = (q + qd + (power*qd)) % MAX_POWER
        if (nr, nq) in board:
            count += 1 
    return count

def mobility(board, color):
    color = 'r' if color == PlayerColor.RED else 'b'
    count = 0
    for r, q in board:
        if board[(r,q)][0] == color:
            count += MAX_COORD
    for r in range(MAX_POWER):
        for q in range(MAX_POWER):
            if not (r,q) in board:
                count += 1
    return count

def connected_components(board, color):
    '''
    returns average size of components
    '''
    board_color = 'r' if color == PlayerColor.RED else 'b'
    connected = []
    visited = set()
    for (r, q) in board.keys():
        if (r, q) not in visited and board[(r,q)][0] == board_color:
            group = set()
            dfs((r, q), board, visited, group, board_color)
            connected.append(group)
    # print(board, connected)
    if not connected:
        return 0
    # Returns size of connected components and largest component size
    return 0.3 * max([len(component) for component in connected]) - 0.5 * len(connected)

def dfs(pos, board, visited, group, color):
    visited.add(pos)
    group.add(pos)
    neighbors = get_neighbors(pos, board, color)
    for neighbor in neighbors:
        if neighbor not in visited and neighbor in board:
            dfs(neighbor, board, visited, group, color)

def get_neighbors(pos, board, color):
    neighbors = []
    power = board[pos][1]
    for d in DIRS:
        dr = d.__getattribute__("r")
        dq = d.__getattribute__("q")
        for p in range(power):
            nr = (pos[0] + dr + (p*dr)) % MAX_POWER
            nq = (pos[1] + dq + (p*dq)) % MAX_POWER
            if (nr, nq) in board:
                if board[(nr, nq)][0] == color:
                    neighbors.append((nr, nq))
    return neighbors

def danger(state):
    board = state.board
    move = state.move
    board_color = 'r' if state.color == PlayerColor.RED else 'b'
    opponent_color = 'r' if board_color == 'b' else 'r'
    danger = 0
    if isinstance(move, SpawnAction):
        cell = (move.cell.__getattribute__("r"), move.cell.__getattribute__("q"))
        for (r, q) in board.keys():
            if cell in get_neighbors((r, q), board, board_color):
                danger += 1
            if cell in get_neighbors((r, q), board, opponent_color):
                danger -= 2
    # if isinstance(move, SpreadAction):
    #     # only consider spreads with one power
    #     next_pos = move.cell + move.direction
    #     cell = (next_pos.r, next_pos.q)
    #     if board.get(cell)[1] == 1: 
    #         direction = move.direction
    #         dr, dq = direction.__getattribute__('r'), direction.__getattribute__('q')
    #         new_cell = ((cell[0] + dr) % MAX_POWER, (cell[1] + dq) % MAX_POWER)
    #         for (r, q) in board.keys():
    #             if new_cell in get_neighbors((r, q), board, board_color):
    #                 danger += 1
    #             if new_cell in get_neighbors((r, q), board, opponent_color):
    #                 danger -= 2
    # print(move, move.cell, board, danger)
    return danger

def generate_options(state, color, sort_moves = False):
    """
    Return list of possible moves and their new states for a player at a given board state 
    """
    color_dict = 'r' if color == PlayerColor.RED else 'b'
    board = state.board
    possible_states = []
    # Add all possible Spread moves
    for r, q in board:
        if board[(r,q)][0] == color_dict:
            for d in DIRS:
                # make new board state for each direction
                new_board = board.copy()
                update_board(new_board, r, q, d)
                pos = HexPos(r, q)
                move = SpreadAction(pos, d)
                turn = state.turn
                option = board_state(state.agent_color, new_board, move, turn, None, color)
                option.value = option.weighted_eval()
                if option.valid_state():
                    possible_states.append(option)
    # Add all possible Spawn moves
    for r in range(0, 7):
        for q in range(0, 7):
            if not (r,q) in board:
                new_board = board.copy()
                new_board[(r,q)] = (color_dict, 1)
                pos = HexPos(r, q)
                move = SpawnAction(pos)
                turn = state.turn
                option = board_state(state.agent_color, new_board, move, turn, None, color)
                option.value = option.weighted_eval()
                if option.valid_state():
                    possible_states.append(option)
    if sort_moves:
        return sorted(possible_states, reverse=True)
    return possible_states

def update_board(input: dict[tuple, tuple], r, q, direction: HexDir):
    '''
    updates new board with completed spread move
    '''
    rd = direction.__getattribute__("r")
    qd = direction.__getattribute__("q")
    for power in range(0, input[(r, q)][1]):
        new_r = (r + rd + (power*rd)) % MAX_POWER
        new_q = (q + qd + (power*qd)) % MAX_POWER

        if (new_r, new_q) in input:
            # remove cell if power is equal to max power
            new_power = input[(new_r, new_q)][1] + 1 
            if new_power == MAX_POWER:
                del input[(new_r, new_q)]
            else:
                input[(new_r, new_q)] = (input[(r,q)][0], new_power)
        else:
            input[(new_r, new_q)] = (input[(r,q)][0], 1)

    del input[(r, q)]