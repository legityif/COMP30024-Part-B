# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
import random, math, time



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
        self._state = board_state(board={}, move=None, turn=0, color=self._color)
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
        self._state.turn += 1
        return self.best_minimax_move()

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
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
        if count_color(self._state.board, self._color) - count_color(self._state.board, self._color.opponent) > 8:
            return self.greedy()
        for option in generate_options(self._state):
            # if time.time() - start_time > 5:
            #     return random.choice(best_moves)
            value = self.minimax(state=option, depth=1, color=self._color.opponent, alpha=NEGATIVE_INF, beta=INF)
            # print("OPTION", option.board, str(option.move), value)
            if value > max_value:  
                max_value = value
                best_moves = [option.move]
            elif value == max_value: 
                best_moves.append(option.move)
        if max_value == NEGATIVE_INF:
            return self.random()
        # print([str(move) for move in best_moves])

        # select move with lowest depth from all best moves
        # lowest_depth = NEGATIVE_INF
        # for move in best_moves:
        #     if 
        return random.choice(best_moves)

    def minimax(self, state, depth, color, alpha, beta):
        """
        Return the best move and estimated value of board state using minimax
        """
        if state.game_over() and depth == 1:
            if state.winner_color() == self._color:
                return INF
            else:
                return NEGATIVE_INF
        if depth == MAX_DEPTH:
            return state.minimax_eval()
        maximising = (color == self._color)
        if maximising:
            max_val = NEGATIVE_INF
            for option in generate_options(state):
                val = self.minimax(option, depth + 1, color.opponent, alpha, beta)
                max_val = max(max_val, val)
                alpha = max(alpha, max_val)
                if alpha >= beta:
                    break
            return max_val
        else:
            min_value = INF
            for option in generate_options(state):
                value = self.minimax(option, depth + 1, color.opponent, alpha, beta)
                min_value = min(min_value, value)
                beta = min(beta, min_value)
                if alpha >= beta:
                    break
            return min_value

    def greedy(self):
        best_moves = []
        max_value = NEGATIVE_INF
        for option in generate_options(self._state):
            val = option.power_eval
            if val > max_val:
                best_moves = [option.move]
                max_val = val
            elif val == max_val:
                best_moves.append(option.move)
        return random.choice(best_moves)  

    def random(self):
        return random.choice([option.move for option in generate_options(self._state)])

class board_state:
    def __init__(self, board, move, turn, color):
        self.board = board
        self.move = move
        self.color = color
        self.turn = turn
    
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
        board = self.board
        color = self.color
        # HAS FLAW - if red has power 5 cell, and blue has 5 power 1 cells:
        # eval says blue is favoured, however red is winning if 5 blue cells are lined up for red spread
        # add variable to determine how many cells the highest power cell of color can reach
        our_power = count_power(board, color)
        opponent_power = count_power(board, color.opponent)
        num_our_cells = count_color(board, color)
        num_opponent_cells = count_color(board, color.opponent)
        # IDK
        our_reachable = count_reachable_cells(board, color)
        opponent_reachable = count_reachable_cells(board, color.opponent)
        '''
        Final equation for heuristic value is still to be tested and determined
        '''
        power_w = 1.5
        cell_w = 2.0
        reachable_w = 0.5
        
        value = power_w*(our_power - opponent_power) + cell_w*(num_our_cells - num_opponent_cells) + reachable_w*(our_reachable - opponent_reachable)

        # return a normalised value of our heuristic estimate between -1 and 1
        return value / ((MAX_TOTAL_POWER - 1)*2)

    def minimax_eval(self):
        board = self.board
        color = self.color
        our_power = count_power(board, color)
        opponent_power = count_power(board, color.opponent)
        num_our_cells = count_color(board, color)
        num_opponent_cells = count_color(board, color.opponent)
        if num_our_cells == 0:
            return float("-inf")
        if num_opponent_cells == 0:
            return float("inf")
        return 1.5*(our_power/num_our_cells) - (opponent_power/num_opponent_cells) + num_our_cells - 1.75*num_opponent_cells

    def greedy_eval(self):
        board = self.board
        color = self.color
        our_power = count_power(board, color)
        opponent_power = count_power(board, opponent(color))
        num_our_cells = countColour(board, color)
        num_opponent_cells = countColour(board, opponent(color))
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

def generate_options(state):
    """
    Return list of possible moves and their new states for a player at a given board state 
    """
    color = 'r' if state.color == PlayerColor.RED else 'b'
    board = state.board
    possible_states = []
    # Add all possible Spread moves
    for r, q in board:
        if board[(r,q)][0] == color:
            for d in DIRS:
                # make new board state for each direction
                new_board = board.copy()
                update_board(new_board, r, q, d)
                pos = HexPos(r, q)
                move = SpreadAction(pos, d)
                turn = state.turn + 1
                option = board_state(new_board, move, turn, state.color)
                if option.valid_state():
                    possible_states.append(option)
    # Add all possible Spawn moves
    for r in range(0, 7):
        for q in range(0, 7):
            if not (r,q) in board:
                new_board = board.copy()
                new_board[(r,q)] = (color, 1)
                pos = HexPos(r, q)
                move = SpawnAction(pos)
                turn = state.turn + 1
                option = board_state(new_board, move, turn, state.color)
                if option.valid_state():
                    possible_states.append(option)
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

def get_symmetric(board):
    symmetries = []
    rotation1 = {}
    rotation2 = {}
    rotation3 = {}
    rotation4 = {}
    rotation5 = {}
    rotation6 = {}
    rotation7 = {}
    for r,q in board:
        rotation1[(r,-q+6)] = board[(r,q)]
        rotation2[(-r+6, q)] = board[(r,q)]
        rotation3[(-r+6, -q+6)] = board[(r,q)]
        rotation4[(q, r)] = board[(r,q)]
        rotation5[(-q+6, r)] = board[(r,q)]
        rotation6[(-q+6, -r+6)] = board[(r,q)]
        rotation7[(q, -r+6)] = board[(r,q)]
    symmetries.append(rotation1)
    symmetries.append(rotation2)
    symmetries.append(rotation3)
    symmetries.append(rotation4)
    symmetries.append(rotation5)
    symmetries.append(rotation6)
    symmetries.append(rotation7)
    return symmetries

    possible_moves = generate_options(colour, colour, board, 1)
    possible_moves.sort()
    return possible_moves[0].move