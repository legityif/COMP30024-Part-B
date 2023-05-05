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
        self._board = {}
        self._color = color
        self._colour = "r" if color == PlayerColor.RED else "b"
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
        # assuming there is always a move to be made
        max_value = -INF
        best_moves = []
        visited = {}
        start_time = time.time()
        if countColour(self._board, self._colour) > countColour(self._board, opponent(self._colour))+4:
            return greedy(self._board, self._colour)
        options = generate_options(self._colour, self._colour, self._board, 0)
        for state in options:
            if time.time() - start_time > 5:
                return random.choice(best_moves)
            if countColour(state.board, opponent(self._color)) == 0:
                return state.move
            value = minimax(visited, state.board, depth=0, maximising=False, color=self._colour, alpha=-INF, beta=INF)
            if value >= max_value:
                max_value = value
                best_moves.append(state.move)
        if max_value == -INF:
            return options[0].move
        return random.choice(best_moves)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                if PlayerColor.RED == color:
                    self._board[(cell.r, cell.q)] = ("r", 1)
                else:
                    self._board[(cell.r, cell.q)] = ("b", 1)
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                update_board(self._board, cell.r, cell.q, direction)
                pass

class board_state:
    def __init__(self, board, move, value, colour):
        self.board = board
        self.move = move
        self.value = value
        self.colour = colour
    
    def __lt__(self, other):
        if self.value == other.value:
            self_count, other_count = 0,0
            self_count = countColour(self.board, self.colour)
            other_count = countColour(other.board, other.colour)
            return self_count < other_count
        return self.value > other.value
    

def generate_options(player, color, board, greedy):
    """
    Return list of possible moves and their new states for a player at a given board state 
    """
    possible_moves = []
    # Add all possible Spread moves
    for r, q in board:
        if board[(r,q)][0] == color:
            for d in DIRS:
                # make new board state for each direction
                new_board = board.copy()
                update_board(new_board, r, q, d)
                pos = HexPos(r, q)
                move = SpreadAction(pos, d)
                # NOTE - SINGLE POWER CELL CHECKING
                if board[(r,q)][1] == 1:
                    nr, nq = (r + d.__getattribute__('r')) % MAX_POWER, (q + d.__getattribute__('q')) % MAX_POWER
                    if not (nr, nq) in board:
                        continue
                if greedy:
                    
                    value = greedy_eval(new_board, player)
                else:
                    value = eval(new_board, player, 0)
                option = board_state(new_board, move, value, color)
                if valid_state(new_board):
                    possible_moves.append(option)
    # Add all possible Spawn moves
    for r in range(0, 7):
        for q in range(0, 7):
            if not (r,q) in board:
                new_board = board.copy()
                new_board[(r,q)] = (color, 1)
                pos = HexPos(r, q)
                move = SpawnAction(pos)
                # don't spawn in neighbouring cell of opponent
                # NOTE - leads to fail when losing :( it can't find any moves to make
                # found = False
                # for d in DIRS:
                #     nr, nq = (r + d.__getattribute__('r')) % MAX_POWER, (q + d.__getattribute__('q')) % MAX_POWER
                #     if (nr, nq) in new_board and new_board[(nr,nq)][0] == opponent(color):
                #         found = True
                #         break
                # if found:
                #     continue
                if greedy:
                    value = greedy_eval(new_board, player)
                else:
                    value = eval(new_board, player, 0)
                option = board_state(new_board, move, value, color)
                if valid_state(new_board):
                    possible_moves.append(option)
    if player != color:
        return sorted(possible_moves, reverse=True)
    return sorted(possible_moves)



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

def valid_state(board):
    """
    Return whether the board is a valid state
    """
    return count_power(board, "b") + count_power(board, "r") <= MAX_TOTAL_POWER

def count_power(board, colour):
    '''
    Return count of colour power
    '''
    count = 0
    for player, k in board.values():
        if player == colour:
            count += k
    return count

def countColour(board, colour):
    '''
    Return count of colour tokens
    '''
    count = 0
    for player, k in board.values():
        if player == colour:
            count += 1
    return count

def minimax(visited, board, depth, maximising, color, alpha, beta):
    """
    Return the best move and estimated value of board state using minimax
    """
    if depth == 3:
        return eval(board, color, depth)
    if countColour(board, color) == 0:
        return NEGATIVE_INF
    if countColour(board, opponent(color)) == 0:
        return INF
    if maximising:
        max_value = NEGATIVE_INF
        for state in generate_options(color, color, board, 0):
            str_board = str(state.board)
            if not str_board in visited.keys():
                value = minimax(visited, state.board, depth+1, False, color, alpha, beta)
                visited[str_board] = value
                symmetries = get_symmetric(state.board)
                for board in symmetries:
                    visited[str(board)] = value
            else:
                value = visited[str_board]
            max_value = max(max_value, value)
            alpha = max(alpha, max_value)
            if alpha >= beta:
                break
        return max_value
    else:
        min_value = INF
        for state in generate_options(color, opponent(color), board, 0):
            str_board = str(state.board)
            if not str_board in visited.keys():
                value = minimax(visited, state.board, depth+1, True, color, alpha, beta)
                visited[str_board] = value
                symmetries = get_symmetric(state.board)
                for board in symmetries:
                    visited[str(board)] = value
            else:
                value = visited[str_board]
            min_value = min(min_value, value)
            beta = min(beta, min_value)
            if alpha >= beta:
                break
        return min_value

def opponent(color):
    return 'b' if color == 'r' else 'r'

def greedy_eval(board, color):
    our_power = count_power(board, color)
    opponent_power = count_power(board, opponent(color))
    num_our_cells = countColour(board, color)
    num_opponent_cells = countColour(board, opponent(color))
    return our_power + 0.5*num_our_cells - 2*num_opponent_cells

def eval(board, color, depth):
    our_power = count_power(board, color)
    opponent_power = count_power(board, opponent(color))
    return our_power - opponent_power
    num_our_cells = countColour(board, color)
    num_opponent_cells = countColour(board, opponent(color))
    if num_our_cells == 0:
        return -INF
    if num_opponent_cells == 0:
        return INF
    return 1.5*(our_power/num_our_cells) - (opponent_power/num_opponent_cells) + 1.75*(num_our_cells -  num_opponent_cells)

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

def greedy(board, colour):
    possible_moves = generate_options(colour, colour, board, 1)
    possible_moves.sort()
    return possible_moves[0].move