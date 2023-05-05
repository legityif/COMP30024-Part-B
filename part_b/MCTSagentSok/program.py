# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir,Board, constants
import math
import random

EARLY = 10
MID = 20
LIKELY = 0.75
UNLIKELY = 0.25




class MonteCarloNode:
    def __init__(self,state:Board._state,color:PlayerColor,parent=None,child=None):
        self.board = Board(state)
        self.board._turn_color = color
        self.color = color
        self.child = []
        self.parent = None
        self.visits = 0
        self.vals = 0
        self.score = 0
        self.heuristic = 0
        self.explored_actions = set()
        self.action = None

    def is_leaf(self):
        return len(self.child) == 0
    
    def get_all_moves(self):
        current_player = self.color
        possible_moves = []        
        for cell in self.board._state.keys():
            if self.board[cell].player == current_player:
                for dirr in HexDir:
                    possible_moves.append(SpreadAction(cell,dirr))
        if(self.board._total_power < constants.MAX_TOTAL_POWER):
            possible_moves+=self.get_Possible_Spawn()
        return possible_moves

    def get_Possible_Spawn(self):
        possible_spawn = set()
        for x in range(constants.BOARD_N):
            for y in range(constants.BOARD_N):
                pos = HexPos(x,y)
                if(self.board[pos].power == 0):
                    possible_spawn.add(SpawnAction(pos))
        return list(possible_spawn)
    
    def get_unsafe(self,power:int,cell:HexPos):
        unsafe = set()
        for x in range(power):
            for dirr in HexDir:
                unsafe.add(cell+(dirr*(x+1)))
        return unsafe


    def select_action(self):
        possible_action = set(self.get_all_moves())
        unexplored = list(possible_action-self.explored_actions)
        if(len(unexplored) > 0):
            action = random.choice(unexplored)
            self.explored_actions.add(action)
            return action
        else:
            return None
        
    def select_child(self, exploration_constant:int):
        best_child = None
        best_ucb = -float("inf")
        for child in self.child:
            ucb = child.vals + exploration_constant*(math.sqrt((math.log(self.visits)/child.visits))) + child.score + child.heuristic
            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child
        return best_child
    
    def get_score(self,color:PlayerColor):
        red_score = self.board._color_power(PlayerColor.RED)
        blue_score = self.board._color_power(PlayerColor.BLUE)
        if(color == PlayerColor.RED):
            return red_score - blue_score
        else:
            return blue_score - red_score

    
    def is_terminal(self):
        return self.board.game_over
    
    def simulate(self):
        copy = MonteCarloNode(self.board._state,self.get_opp_color(self.color))
        while(not copy.board.game_over):
            action = random.choice(copy.get_all_moves())
            copy.board.apply_action(action)
            copy.color = copy.get_opp_color(copy.color)
            
        if(copy.board.winner_color==self.color):
            return 1
        if(copy.board.winner_color==self.get_opp_color(self.color)):
            return -1
        else:
            return 0
        
    def get_opp_color(self,color:PlayerColor):
        if(color == PlayerColor.RED):
            return PlayerColor.BLUE
        else:
            return PlayerColor.RED
        
        
        
    


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
        self.root = MonteCarloNode(self.board._state,self._color)

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
                if(self.board._total_power == 0):
                    return SpawnAction(HexPos(3,3))
                return MonteCarloSearch(self.root,100,math.sqrt(2))
            case PlayerColor.BLUE:
                if(self.board._total_power == 0):
                    return SpawnAction(HexPos(3,3))
                # This is going to be invalid... BLUE never spawned!
           
                return MonteCarloSearch(self.root,100,math.sqrt(2))

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


def MonteCarloSearch(root:MonteCarloNode,num_iterations:int,exploration_constant:int):
    copy_root = MonteCarloNode(root.board._state,root.color)

    for i in range(num_iterations):
        #select 
        curr = copy_root
        action = curr.select_action()
        while(action == None):
            curr = curr.select_child(math.sqrt(2))
            action = curr.select_action()
        new_node = MonteCarloNode(curr.board._state,curr.color)
        curr.child.append(new_node) 
        new_node.parent = curr
        if(not new_node.is_terminal()):
            #expand
            new_node.action = action
            new_node.board.apply_action(action)
            #simulate
            result = new_node.simulate()
            #backpropogate
            while(new_node is not None):
                new_node.visits+=1
                new_node.vals+=result
                new_node = new_node.parent
    best_child = max(copy_root.child,key = lambda child:child.vals/child.visits)
    
    return best_child.action