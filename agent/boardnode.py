from referee.game import PlayerColor, Action, PlaceAction, Coord
from .utils import board_to_string, string_to_board, generate_possible_moves, place_tetromino, render_board, heuristic_evaluation

class BoardNode:
    def __init__(self, board_dict: dict[Coord, PlayerColor], color: PlayerColor, parent: 'BoardNode' = None, action: 'PlaceAction' = None) -> None:
        self.board_str = board_to_string(board_dict) # Storing a string
        self.parent = parent
        self.action = action
        self.win = 0
        self.visit = 0
        self.loss = 0
        self.draw = 0
        self.uct = heuristic_evaluation(board_dict, color)
        self.depth = 0
        self.terminal = False
        self.children = [] # List of children nodes
        self.mycolor = color

    def __hash__(self):
        return self.board
    
    def __eq__(self, other) -> bool:
        return self.board_str == other.board_str
    
    def terminal(self) -> bool:
        return self.terminal

    def print_tree(self, level=0):
        print("Depth: ", level, " | Visited: ", self.visit, " | UCT: ", self.win, "/", self.win + self.loss + self.draw, " ~ ", self.uct)
        if self.visit > 0:
            print(render_board(string_to_board(self.board_str), True))
        for child in self.children:
            child.print_tree(level + 1)