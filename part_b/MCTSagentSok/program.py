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


global_row = {}
global_col = {}
global_diagnol = {}


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
        self.number = None

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
            ucb = child.vals + exploration_constant*(math.sqrt((math.log(self.visits)/child.visits))) + 0.5*child.get_score(child.color)
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

    def get_good_move(self):
        best_move = None
        best_score = -float("inf")
        for action in self.get_all_moves():
            self.board.apply_action(action)
            if(self.get_score(self.color)>best_score):
                best_move = action
                best_score = self.get_score(self.color)
            self.board.undo_action()
        return best_move
        
    
    def simulate(self):
        copy = MonteCarloNode(self.board._state,self.get_opp_color(self.color))
        while(not copy.board.game_over):
            action = copy.get_good_move()
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
        
    def number_of_lines_simple(self):
        ally_row = []
        ally_col = []
        ally_diagnol = []
        enemy_set = set()
        for pos,cellstate in self.board._state.items():
            if(cellstate.player == self.color):
                ally_row.append(pos.r)
                ally_col.append(pos.q)
                ally_diagnol += global_diagnol[pos.r]
        for pos,cellstate in self.board._state.items():
            if(cellstate.player!=self.color):
                if(pos.r in ally_row or pos.q in ally_col or pos in ally_diagnol):
                    enemy_set.add(pos)
        return len(enemy_set)


    def number_of_lines_complex(self):
        ally_cell = []
        enemy_set = set()
        addition_count = 0
        for pos,cellstate in self.board._state.items():
            if(cellstate.player == self.color):
                if(cellstate.power<=3):
                    least_r = pos.r - cellstate.power
                    most_r = pos.r + cellstate.power
                    least_q = pos.q - cellstate.power
                    most_q = pos.q + cellstate.power
                    ally_cell+=global_row[pos.r][least_r:most_r]
                    ally_cell+=global_col[pos.q][least_q:most_q]
                    for i in range(cellstate.power):
                        ally_cell += pos+HexDir.Down*(i+1)
                        ally_cell += pos+HexDir.Up*(i+1)
                else:
                    addition_count += self.number_of_lines_simple()
        for pos,cellstate in self.board._state.items():
            if(cellstate.player!=self.color):
                if(pos in ally_cell):
                    enemy_set.add(pos)
        return len(enemy_set) + addition_count
        
    # def pre_expand(self):
    #     i=0
    #     for action in self.get_all_moves():
    #         i+=1
    #         child = MonteCarloNode(self.board._state,self.color)
    #         self.child.append(child)
    #         child.parent = self
    #         child.board.apply_action(action)
    #         child.action = action
    #         child.number = i
    #         child.heuristic = 0.3*child.number_of_lines_complex() + 0.7*child.get_score(child.color)

    # def select_child(self, exploration_constant):
    #     best_child = None
    #     best_ucb = -float("inf")
    #     for child in self.child:
    #         if(self.visits == 0 or child.visits == 0):
    #             ucb = float("inf")
    #         else:
    #             ucb = child.vals + child.heuristic + exploration_constant*(math.sqrt(math.log(self.visits)/child.visits))
            
    #         if(ucb > best_ucb):
    #             best_ucb = ucb
    #             best_child = child
    #     return best_child
    


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
        generate_cheat_columns()
        generate_cheat_diagnols()
        generate_cheat_rows()

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
                return MonteCarloSearch(self.root,100,10)
            case PlayerColor.BLUE:
                if(self.board._total_power == 0):
                    return SpawnAction(HexPos(3,3))
                # This is going to be invalid... BLUE never spawned!
           
                return MonteCarloSearch(self.root,100,10)

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
    if(copy_root.board._color_power(copy_root.color) == copy_root.board._player_cells(copy_root.get_opp_color(copy_root.color))):
        return copy_root.get_good_move()
    else:
        for i in range(num_iterations):
            #select 
            curr = copy_root
            action = curr.select_action()
            if (action == None):
                while(curr!=None):
                    if(curr.select_child(math.sqrt(2)) == None):
                        break
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
         
        best_child = max(copy_root.child,key = lambda child:child.vals)
   
        return best_child.action



# def MonteCarloSearch(root:MonteCarloNode, num_iterations:int, exploration_constant:int):
#     copy_root = MonteCarloNode(root.board._state,root.color)
#     copy_root.pre_expand()
#     for i in range(num_iterations):
#         child = copy_root.select_child(10)

#         result = child.simulate()
#         while(child is not None):
#             child.visits+=1
#             child.vals += result
#             child = child.parent
#     best_child = max(copy_root.child,key=lambda child:child.vals)
#     return best_child.action
    


def generate_cheat_rows():
    dictt ={}
    for x in range(constants.BOARD_N):
        listt = []
        for y in range(constants.BOARD_N):
            listt.append(HexPos(x,y))
        dictt[x] = listt
    global global_row
    global_row = dictt

def generate_cheat_columns():
    dictt = {}
    for x in range(constants.BOARD_N):
        listt = []
        for y in range(constants.BOARD_N):
            listt.append(HexPos(y,x))
        dictt[x] = listt
    global global_col
    global_col = dictt

def generate_cheat_diagnols():
    dictt = {}
    for x  in range(constants.BOARD_N):
        listt = []
        starting_pos = HexPos(0,x)
        for y in range(constants.BOARD_N):
            listt.append(starting_pos+(HexDir.Down*y))
        dictt[x] = listt
    global global_diagnol
    global_diagnol = dictt