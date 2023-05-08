# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

BOARD_SIZE = 7
NUM_PLAYTHROUGHS = 1000

import random, math
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from collections import deque
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
        self.possible_moves = []


class boardState:
    def __init__(self, color, turn, board=None):
        # self._color should be the player that just made the move!
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
        # color rn should be the player that just made the move!
        # print("\n in board state: -------------------------\n")
        # print("in board state, turn is ", self._turn, "board is", self._board, "color is", self._color)
        player, enemy = 0, 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self._board[r][c] is not None:
                    if self._board[r][c][0]==self._color:
                        player += self._board[r][c][1]
                    else:
                        enemy += self._board[r][c][1]
        #print("player: ", player, "enemy: ", enemy)
        if enemy==0 and self._turn!=1:
            return [True, 1]
        if (player==0 and self._turn != 1) or (enemy==0 and self._turn!=1) or (player==0 and enemy==0 and (self._turn!=0)) or self._turn==343:
            return [True, 0]
        return [False, 0]
        
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
    
    def simulate(self, node, player):
        #simulate the game using a strategy, could be random moves, the first move should be player's move
        # print("\nsimulating: ----------------------------")
        # print("turn is ", node.state._turn, "player is: ", player)
        # print("in simulate, board is", node.state._board)
        #print("in simulate, color is ", player)
        curr_node = node
        curr_player = player
        #print("turn is: ", curr_turn)
        while curr_node.state.reachedTerminal()[0] == False and curr_node.state._turn < node.state._turn + 15:
            #print("\nnot in terminal state, player is:", curr_player)
            possible_moves = self.generate_moves(curr_player, curr_node.state)

            # greedy not very good?
            # best_eval = -10000 if curr_player == self._color else 10000
            # best_moves = []
            # for move in possible_moves:
            #     dummy_state = self.applyMovetoBoard(curr_node.state, move, curr_player)
            #     power = self.power_eval_fn(dummy_state)
            #     if curr_player == self._color:
            #         if power > best_eval:
            #             best_moves = [move]
            #             best_eval = power
            #         elif power == best_eval:
            #             best_moves.append(move)
            #     elif curr_player != self._color:
            #         if power < best_eval:
            #             best_moves = [move]
            #             best_eval = power
            #         elif power == best_eval:
            #             best_moves.append(move)

            # best_move = self.randomMove(best_moves)
            #print("turn: ", curr_node.state._turn, "player: ", curr_player, "best_eval: ", best_eval)

            best_move = self.randomMove(possible_moves)
            if best_move is None:
                print("error no best move")
                return None

            #print("move is: ", best_move)
            new_state = self.applyMovetoBoard(curr_node.state, best_move, curr_player)
            #print("new board: ", new_state._board)
            curr_node = Node(best_move, new_state)
            curr_player = PlayerColor.RED if PlayerColor.BLUE == curr_player else PlayerColor.BLUE
        
        # calculate result, every win/loss is calculated in terms of self.player (our actual agent color)
        #print("---after simulation, turn is ", curr_node.state._turn)
        # if curr_node.state._turn == 343:
        #     print("draw")
        #     return 0
        result = curr_node.state.reachedTerminal()
        if result[1] == 1:
            # print("won this one")
            return 1
        if self.power_eval_fn(curr_node.state) > 10:
            #print("positive power")
            return 0.9
        elif self.power_eval_fn(curr_node.state) > 5:
            #print("somewhat positive power")
            return 0.25
        else:
            #print("negative")
            return 0
        
    
    def selection(self, root, player):
        # select using UCB, assume that when this function is called, all children of root node are expanded
        # all nodes in the tree have a max_UCB value of their subtree, and every node has their own UCB value 
        #TODO: need to deal with the case where the selected node is fully expanded
        
        #print("-------------------in selection, tree max: ", root.max_subtree_UCB)
        node = root
        while len(node.children) > 0:
            max_UCB_child = None
            for child in node.children:
                #print("for this child, color is: ", child.state._color, ",UCB is", child.UCB)
                if abs(child.max_subtree_UCB - root.max_subtree_UCB) <= 0.0001:
                    max_UCB_child = child
                    break

            if max_UCB_child == None:
                print("error in selection")
                return None
            
            #print("here")
            node = max_UCB_child
            #print("node UCB", node.UCB)
            if abs(node.UCB - root.max_subtree_UCB) <= 0.0001:
                #print("return node in selection, selected node is on turn ", node.state._turn)
                return node
            
            # result = []
            # queue = deque([root])
            # while queue:
            #     q_node = queue.popleft()
            #     result.append(q_node)
                
            #     for child in q_node.children:
            #         queue.append(child)

            # for child in result:
            #     print("child is on turn: ", child.state._turn, "child has UCB: ", child.UCB)


        print("best UCB not found, error")
        quit()

        return None
    
    def calculate_UCB(self, node):
        constant = math.sqrt(2)
        if node.parent == None:
            #print("root node")
            return 0
        if node.visits==0 or node.parent.visits==0:
            print("division error in calculate_UCB")
            return None
        return node.wins / node.visits + constant * math.sqrt(math.log(node.parent.visits)/node.visits)
    
    def expand(self, node, player):
        # Add one child node to the given node, using an expansion strategy
        # player is the player that just made the move
        next_player = PlayerColor.RED if PlayerColor.BLUE==player else PlayerColor.BLUE

        if len(node.possible_moves) == 0 and len(node.children) == 0:
            node.possible_moves = self.generate_moves(next_player, node.state)

        if len(node.possible_moves) == 0 and len(node.children) != 0:
            print("error in expand, no more possible moves")
            
            # fallback
            for child in node.children:
                return self.expand(child, next_player)

        move = self.randomMove(node.possible_moves)
        node.possible_moves.remove(move)
        new_state = self.applyMovetoBoard(node.state, move, next_player)
        new_node = Node(move, new_state, node)
        node.children.append(new_node)

        return new_node
    
    def backpropagate(self, node, value, root):
        # Propagate upwards, updating the wins / visits, also update the max_UCB and its own UCB, 
        # as well as the direct children's UCB of each node on the way up

        # print("\n in propagate, node is on turn: ", node.state._turn, ", player color is: ", node.state._color, "move is: ", node.move, "value is: ", value)
        # print("before anything is done: here are the values")
        # result = []
        # queue = deque([root])
        # while queue:
        #     node = queue.popleft()
        #     result.append(node)
            
        #     for child in node.children:
        #         queue.append(child)

        # for child in result:
        #     if child == root:
        #         #print("root node")
        #         continue
        #     else:
        #         #print("child is on turn: ", child.state._turn, "child has UCB: ", child.UCB, "child has move: ", child.move, "wins: ", child.wins, "visits: ", child.visits, "parent wins: ", child.parent.wins, "parent visits: ", child.parent.visits)
        #         continue


        # first update all the wins and visits by propagating upwards
        curr_node = node
        while curr_node is not None:
            #print("curr_node: turn", curr_node.state._turn, "player color: ", curr_node.state._color, "move: ", curr_node.move, "self color: ", self._color)
            curr_node.visits += 1
            #print("value is: ", value, "curr node wins: ", curr_node.wins)
            curr_node.wins += value if curr_node.state._color == self._color else 1-value
            #print("value is: ", value, "curr node wins: ", curr_node.wins)
            curr_node = curr_node.parent
        
        # print("\nafter the first backpropagation")
        # for child in result:
        #     if child == root:
        #         print("root node")
        #     else:
        #         print("child is on turn: ", child.state._turn, "child has UCB: ", child.UCB, "child has move: ", child.move, "wins: ", child.wins, "visits: ", child.visits, "parent wins: ", child.parent.wins, "parent visits: ", child.parent.visits)

        # Then do backpropagation again, this time updating the UCB values
        # TODO: might be doing double updates on some nodes, could speed up? 
        curr_node = node
        while curr_node is not None:
            # update UCB of any direct children first
            max_children_UCB = 0
            for child in curr_node.children:
                new_UCB = self.calculate_UCB(child)
                if (new_UCB < child.UCB):
                    print("error in backpropagation, should not get lower UCB")
                child.UCB = new_UCB
                child.max_subtree_UCB = max(child.max_subtree_UCB, child.UCB)
                max_children_UCB = max(max_children_UCB, child.max_subtree_UCB)

            # then update the curr_node's own UCB
            curr_node_new_UCB = self.calculate_UCB(curr_node)
            # if (curr_node_new_UCB < curr_node.UCB):
            #     # if this curr_node was the highest UCB of the parent subtree, then we may need to update the maxes upwards
            #     print("error in backpropagation, curr_node's new UCB should not be lower!")
            #     print("error node is on turn: ", curr_node.state._turn, "with move: ", curr_node.move)
            curr_node.UCB = curr_node_new_UCB
            curr_node.max_subtree_UCB = max(max_children_UCB, curr_node.UCB)

            curr_node = curr_node.parent

        # print("after propagation, max UCB in the tree is: ", root.max_subtree_UCB)
        # result = []
        # queue = deque([root])
        # while queue:
        #     node = queue.popleft()
        #     result.append(node)
            
        #     for child in node.children:
        #         queue.append(child)

        # for child in result:
        #     # if child == root:
        #     #     print("root node")
        #     # else:
        #     #     print("child is on turn: ", child.state._turn, "child has UCB: ", child.UCB, "child has move: ", child.move, "wins: ", child.wins, "visits: ", child.visits, "parent wins: ", child.parent.wins, "parent visits: ", child.parent.visits)
        #     if child.UCB == root.max_subtree_UCB:
        #         print("max child found, move is: ", child.move)
        #         dummy_child = child
        #         while dummy_child:
        #             print("dummy_child, turn and move: ", dummy_child.state._turn, dummy_child.move)
        #             dummy_child = dummy_child.parent
        # print("propagate done -------------------------------------------\n")
        
        return

    
    def MCTS(self, state, player):
        # Do play through once for all the children of root node, player in the argument is the player that will move next
        # each node's state._color is the player that JUST made the move 
        random.seed(1)
        print("|||| MCTS: -----------------------------------\n")
        root = Node(None, state)
        root.state._color = PlayerColor.RED if player==PlayerColor.BLUE else PlayerColor.BLUE

        moves = self.generate_moves(player, state)
        for move in moves:
            
            #print("in MCTS, move is: ", move, "player is: ", player)
            child_state = self.applyMovetoBoard(state, move, player)
            #print("turn is: ", child_state._turn)
            child_node = Node(move, child_state, root)
            root.children.append(child_node)

            # start with opponent's move in the simulation
            result = self.simulate(child_node, PlayerColor.RED if player==PlayerColor.BLUE else PlayerColor.BLUE)

            # propagate results and deal with initila UCB
            root.visits += 1
            root.wins += result

            child_node.visits += 1
            child_node.wins += result
            child_node.max_subtree_UCB = child_node.UCB = self.calculate_UCB(child_node)

            root.max_subtree_UCB = max(root.max_subtree_UCB, child_node.max_subtree_UCB)
        
        # total = 0
        # for child in root.children:
        #     #print("child node wins:", child.wins, "visits: ", child.visits)
        #     total += child.wins
        # print("total is:", total, "root total: ", root.wins, "root visits: ", root.visits, "max_UCB: ", root.max_subtree_UCB)

        # do a number of playthroughs using MCTS algorithm
        for i in range(NUM_PLAYTHROUGHS):
            #print("iteration number: ", i)
            
            # TODO:  need to think about what happens with player color!
            node = self.selection(root, player)
            #print("selected node has UCB: ", node.UCB, "root max UCB: ", root.max_subtree_UCB)
            #print("color of node is:", node.state._color)

            new_node = self.expand(node, node.state._color)
            #print("expanded node is: ", new_node.state._board, " color is: ", new_node.state._color)

            next_player = PlayerColor.RED if new_node.state._color == PlayerColor.BLUE else PlayerColor.BLUE
            result = self.simulate(new_node, next_player)

            self.backpropagate(new_node, result, root)
            
            # if i == NUM_PLAYTHROUGHS-1:
            #     result = []
            #     queue = deque([root])
            #     while queue:
            #         q_node = queue.popleft()
            #         result.append(q_node)
                    
            #         for q_child in q_node.children:
            #             queue.append(q_child)

            #     for q_child in result:
            #         if q_child == root:
            #             print("root node")
            #         else:
            #             print("child is on turn: ", q_child.state._turn, "child has UCB: ", q_child.UCB, "child has move: ", q_child.move, "wins: ", q_child.wins, "visits: ", q_child.visits, "parent wins: ", q_child.parent.wins, "parent visits: ", q_child.parent.visits)

        # find the best move
        best_child = max(root.children, key=lambda x: x.wins / x.visits if x.visits != 0 else 0)
        #print("best move found:", best_child.state._board, "color is: ", best_child.state._color)
            
        if best_child == None:
            print("error no best move")
            return None
        else:
            print("power difference is: ", self.power_eval_fn(root.state))
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
    
    def randomMove(self, possible_moves):
        rand_move = random.randint(0, len(possible_moves)-1)
        return possible_moves[rand_move]
        
    def applyMovetoBoard(self, state, action, curr_player):
        new_state = boardState(curr_player, state._turn+1, state._board)
        new_board = new_state._board
        match action:
            case SpawnAction(cell):
                # for both agent colours, add to board 
                if PlayerColor.RED == curr_player:
                    new_board[cell.r][cell.q] = (curr_player, 1)
                if PlayerColor.BLUE == curr_player:
                    new_board[cell.r][cell.q] = (curr_player, 1)
                return new_state
            case SpreadAction(cell, direction):
                orig_cell = cell
                if PlayerColor.RED == curr_player:
                    # call spread to update board
                    self.spreadInDir(new_board, direction, cell, orig_cell, new_board[cell.r][cell.q][1], curr_player)
                if PlayerColor.BLUE == curr_player:
                    # call spread to update board
                    self.spreadInDir(new_board, direction, cell, orig_cell, new_board[cell.r][cell.q][1], curr_player)
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
