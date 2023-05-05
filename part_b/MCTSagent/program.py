# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7
MINIMAX_DEPTH = 3
NUM_PLAYTHROUGHS = 10
LATE_GAME = 50

import random, math
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
DIRECTIONS = (HexDir.Up, HexDir.UpLeft, HexDir.UpRight, HexDir.Down, HexDir.DownLeft, HexDir.DownRight)

class Node:
    def __init__(self, move, state, parent=None):
        self.move = move
        self.state = state
        self.parent = parent
        self.children = []
        self.wins = 0.0
        self.visits = 0
        self.UCB = 0
        self.max_subtree_UCB = 0


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
        if color==PlayerColor.RED:
            self._enemy = PlayerColor.BLUE
        else:
            self._enemy = PlayerColor.RED
        self._turn = 0
        self._state = boardState(self._color, self._turn, None)
        match color:
            case PlayerColor.RED:
                print("Testing: MCTS Agent is playing as red")
            case PlayerColor.BLUE:
                print("Testing: MCTS Agent is playing as blue")
    
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
                return self.MCTS(self._state, self._color)
            case PlayerColor.BLUE:       
                self._turn += 1 
                return self.MCTS(self._state, self._color) 
    
    def simulate(self, node):
        #simulate the game using a strategy, could be random moves
        return None
    
    def selection(self, node):
        # select using UCB
        return None
    
    def expand(self, node):
        # Add one child node to the given node, using an expansion strategy
        return None
    
    def backpropagate(self, node, value):
        # Propagate upwards, updating the wins / visits, also update the max_UCB and its own UCB, 
        # as well as the direct children's UCB of each node on the way up

        return None

    
    def MCTS(self, state, player):
        # Do play through once for all the children of root node
        root = Node(None, state)

        moves = self.generate_moves(player, state)
        for move in moves:
            child_state = self.applyMovetoBoard(state, move, player)
            child_node = Node(move, child_state)
            root.children.append(child_node)

            self.simulate(child_node)
        
        # do a number of playthroughs using MCTS algorithm
        for i in range(NUM_PLAYTHROUGHS):

            node = self.selection(root)

            new_node = self.expand(node)

            result = self.simulate(new_node)

            self.backpropagate(new_node, result)

        # find the best move
        best_child = max(root.children, key=lambda x: x.wins / x.visits if x.visits != 0 else 0)
            
        if best_child == None:
            print("error no best move")
            return None
        else:
            return best_child.move
    
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
        board = state._board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if board[r][c][0] == self._color:
                        player_power += board[r][c][1]
                    else:
                        enemy_power += board[r][c][1]
        # consider how many moves you can make compared to enemy
        spawn_mobility_diff = len(self.generate_spawns(self._color, state)) - len(self.generate_spawns(self._enemy, state))
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