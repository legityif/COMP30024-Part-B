# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board, constants
import random
import math
class MonteCarloNode:
    def __init__(self,state:Board._state,winner:PlayerColor,loser:PlayerColor):
        self.parent = None
        self.child = []
        self.action = None
        self.visit = 0
        self.val = 0
        self.board = Board(state)
        self.winner = winner
        self.loser = loser
        self.action = None
        self.explored_action = set()
        self.possible_moves = []
    def get_all_moves(self,color:PlayerColor):
        #the function takes in a color and get those set of moves
        #in pre_expand get all move is always the color of the root
        #in simulate this should be the color of the board turn
        current_player = color
        possible_moves = []        
        for cell in self.board._state.keys():
            if self.board[cell].player == current_player:
                for dirr in HexDir:
                    possible_moves.append(SpreadAction(cell,dirr))
        if(self.board._total_power < constants.MAX_TOTAL_POWER):
            possible_moves+=self.get_Possible_Spawn()
        return possible_moves
    
    def ally_close(self,wanted_winner:PlayerColor):
        count=0
        visited = [[False] * constants.BOARD_N for _ in range(constants.BOARD_N)]
        def dfs(hex_pos):
            visited[hex_pos.r][hex_pos.q] = True
            for direction in HexDir:
                new_pos = hex_pos+direction
                if (self.board[HexPos(new_pos.r,new_pos.q)].player == wanted_winner and not visited[new_pos.r][new_pos.q]):
                    nonlocal count
                    count+=1
                    dfs(new_pos)

        for pos,cell in self.board._state.items():
            if(cell.player == wanted_winner and not visited[pos.r][pos.q]):
                initial_pos = pos
                dfs(initial_pos)
        return count

    
    def get_good_move(self,wanted_winner:PlayerColor):
        best_move = None
        best_score = -float("inf")
        for action in self.get_all_moves(wanted_winner):
            self.board.apply_action(action)
            if(self.board.winner_color == wanted_winner):
                self.board.undo_action()
                return action
            if(self.get_score()>best_score):
                best_move = action
                best_score = self.get_score()
            self.board.undo_action()
            
        return best_move
    
    def get_Possible_Spawn(self):
        possible_spawn = set()
        for x in range(constants.BOARD_N):
            for y in range(constants.BOARD_N):
                pos = HexPos(x,y)
                if(self.board[pos].power == 0):
                    possible_spawn.add(SpawnAction(pos))
        return list(possible_spawn)
    
    


    def pre_expand(self,simulation:int,exploration_constant:int):
        possible_actions = self.get_all_moves(self.winner)
        for action in possible_actions:
            child = MonteCarloNode(self.board._state,self.winner,self.loser)
            child.board._turn_color = self.board._turn_color
            child.parent = self
            self.child.append(child)
            child.action = action
            self.explored_action.add(action)
            child.board.apply_action(action)
            if(child.board.winner_color == self.winner):
                child.val = float("inf")
            if(type(action) == SpawnAction):
                if(is_safe(child,action.cell)):
                    child.val += 0.01
                elif(is_unsafe(child,child.action.cell)):
                    child.val -= 0.01
                else:
                    child.val += 0.005
            else:
                if(is_safe(child,action.cell+action.direction)):
                    child.val+=0.01
            child.val += 0.01*child.board._color_power(self.winner)
            child.visit+=1
            self.visit+=1

    def select_move(self):
        if(len(list(set(self.possible_moves) - self.explored_action))) > 0:
            return random.choice(list(set(self.possible_moves) - self.explored_action))
        return None
    
    def get_score(self):
        return self.board._color_power(self.winner) - self.board._color_power(self.loser)

    def simulate(self,simulation,wanted_winner:PlayerColor):
        if(wanted_winner==PlayerColor.RED):
            loser_color = PlayerColor.BLUE
        else:
            loser_color = PlayerColor.RED
        copy = MonteCarloNode(self.board._state,wanted_winner,loser_color)
        # if(copy.get_score()>=1):
        #     print(copy.board.render())
        #     print(copy.get_score())
        copy.board._turn_color = self.board._turn_color
        start = 0
        while(not copy.board.game_over and start <= simulation):
            action = copy.get_good_move(copy.board._turn_color)
            copy.board.apply_action(action)
            start+=1
        
        # if(start>=simulation):
        #     if(copy.get_score() < -constants.MAX_CELL_POWER):
        #         return -1
        #     elif(copy.get_score() > constants.MAX_CELL_POWER):
        #         return 1
        #     elif(wanted_winner==PlayerColor.RED):
        #         if(copy.get_score() < 0):
        #             return -0.25 + 0.1*copy.get_score()
        #         elif(copy.get_score() > 0):
        #             return 0.25 +  0.1*copy.get_score()
        #     elif(wanted_winner == PlayerColor.BLUE):
        #         if(copy.get_score() < -1):
        #             return -0.25 +  0.1*copy.get_score()
        #         elif(copy.get_score() > 1):
        #             return 0.25 +  0.1*copy.get_score()
        #     else:
        #         return 0
        if(copy.board.winner_color==wanted_winner):
            return 1.25
        if(copy.board.winner_color==loser_color):
            return -1.25
        else:
            return 0
    
    def select_child(self,exploration_constant:int,losing:bool):
        best_ucb = -float("inf")
        best_child = None
        
        curr_power = self.get_score()
        for child in self.child:
            child_ucb = child.val/child.visit + exploration_constant * math.sqrt(math.log(self.visit)/child.visit) 
            if(child_ucb>best_ucb):
                best_ucb = child_ucb
                best_child = child
            if(child_ucb==best_ucb):
                best_ucb = child_ucb
                best_child = random.choice([best_child,child])
        return best_child
    
    def select_move(self):
        if(len(list(set(self.possible_moves) - self.explored_action))) > 0:
            return random.choice(list(set(self.possible_moves) - self.explored_action))
        return None


    def greedy_simulate(self,simulation,wanted_winner:PlayerColor):
        if(wanted_winner==PlayerColor.RED):
            loser_color = PlayerColor.BLUE
        else:
            loser_color = PlayerColor.RED
        copy = MonteCarloNode(self.board._state,wanted_winner,loser_color)
        copy.board._turn_color = self.board._turn_color
        start = 0

        while(not copy.board.game_over and start <= simulation):
            action = copy.get_good_move(copy.board._turn_color)
            copy.board.apply_action(action)
            start+=1

        # if(start>=simulation):
        #     if(wanted_winner==PlayerColor.RED):
        #         if(copy.get_score() < 0):
        #             return -0.25 + 0.1*copy.get_score()
        #         elif(copy.get_score() > 0):
        #             return 0.25 +  0.1*copy.get_score()
        #     elif(wanted_winner == PlayerColor.BLUE):
        #         if(copy.get_score() < -1):
        #             return -0.25 +  0.1*copy.get_score()
        #         elif(copy.get_score() > 1):
        #             return 0.25 +  0.1*copy.get_score()
        #     else:
        #         return 0
        if(copy.board.winner_color==wanted_winner):
            return 1 
        if(copy.board.winner_color==loser_color):
            return -1
        else:
            return 0




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
        self.board = Board()
        if(self._color==PlayerColor.RED):
            self._loser = PlayerColor.BLUE
        else:
            self._loser = PlayerColor.RED
        self.turn_count = 0
        self.root = MonteCarloNode(self.board._state,self._color,self._loser)
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        match self._color:
            case PlayerColor.RED:
                self.turn_count+=2
                if(self.board._total_power == 0):
                    return SpawnAction(HexPos(3,3))
                return MonteCarloSearch(self.root,300,20,2,self.turn_count)
            case PlayerColor.BLUE:
                self.turn_count+=2
                if(self.board._color_power(self._color) == 0):
                    return safeSpawn(self.board,self._color)
                self.root.board._turn_color = PlayerColor.BLUE
                return MonteCarloSearch(self.root,300,20,math.sqrt(2),self.turn_count)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                self.board.apply_action(SpawnAction(cell))
                self.root.board = Board(self.board._state)
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                self.board.apply_action(SpreadAction(cell,direction=direction))
                self.root.board = Board(self.board._state)
                pass


def MonteCarloSearch(root:MonteCarloNode,num_iterations:int,simulations:int,exploration_constant:int,turn_count:int):
    copy_root = MonteCarloNode(root.board._state,root.winner,root.loser)
    copy_root.board._turn_color = root.board._turn_color
    copy_root.pre_expand(simulations,exploration_constant)
    losing = False
    # if(copy_root.get_score() >= constants.MAX_CELL_POWER):
    #     return copy_root.get_good_move(copy_root.winner)
    for i in range(num_iterations):
        child = copy_root.select_child(exploration_constant,losing)
        if(len(child.explored_action) == 0):
            child.possible_moves = child.get_all_moves(child.board._turn_color)
        action = child.select_move()

        while(action == None):
            child = child.select_child(exploration_constant,losing)
            if(len(child.explored_action) == 0):
                child.possible_moves = child.get_all_moves(child.board._turn_color)
            action = child.select_move()
        expanded_node = MonteCarloNode(child.board._state, copy_root.winner,copy_root.loser)
        expanded_node.board._turn_color = child.board._turn_color
        #now we have a child node and its expansion, the child should append the new action and the expanded node should apply the action
        child.explored_action.add(action)
        expanded_node.board.apply_action(action)
        expanded_node.parent = child
        child.child.append(expanded_node)
        expanded_node.action = action

        result = expanded_node.simulate(simulations,copy_root.winner)
      
        while(expanded_node is not None):
            expanded_node.visit+=1
            expanded_node.val += result
            expanded_node = expanded_node.parent

    #assuming better child = more visits
    best_child = max(copy_root.child, key=lambda child: (child.visit, child.val))

    return best_child.action


def safeSpawn(board:Board,color:PlayerColor):
    unsafe = []
    safe = []
    for pos,cell in board._state.items():
        unsafe.append(pos)
        for dirr in HexDir:
            unsafe.append(pos+dirr)
    for x in range(constants.BOARD_N):
        for y in range(constants.BOARD_N):
            pos = HexPos(x,y)
            if(pos not in unsafe):
                safe.append(pos)
    return SpawnAction(random.choice(safe))




def is_safe(node:MonteCarloNode,pos:HexPos):
    for dirr in HexDir:
        new_pos = pos+dirr
        if(node.board[new_pos].player == node.winner):
            return True
    return False

def is_unsafe(node:MonteCarloNode,pos:HexPos):
    if(node.winner==PlayerColor.RED):
        opponent = PlayerColor.BLUE
    else:
        opponent = PlayerColor.RED
    for dirr in HexDir:
        if(node.board[pos+dirr].player == opponent):
            return True
    return False