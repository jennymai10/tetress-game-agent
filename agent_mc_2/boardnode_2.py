from referee.game import PlayerColor, Action, PlaceAction, Coord
from .utils_2 import board_to_string, string_to_board, generate_possible_moves, place_tetromino, render_board

class BoardNode:
    def __init__(self, board_dict: dict[Coord, PlayerColor], color: PlayerColor, parent: 'BoardNode' = None, action: 'PlaceAction' = None) -> None:
        self.board_str = board_to_string(board_dict) # Storing a string
        self.parent = parent
        self.action = action
        self.win = 0
        self.visit = 0
        self.loss = 0
        self.draw = 0
        self.uct = float('inf')
        self.terminal = False
        self.children = [] # List of children nodes
        self.mycolor = color

    def __hash__(self):
        return self.board
    
    def __eq__(self, other) -> bool:
        return self.board_str == other.board_str
    
    def terminal(self) -> bool:
        return self.terminal
    
    # def get_children(self) -> list:
    #     board_dict = string_to_board(self.board_str)
    #     for act in generate_possible_moves(board_dict, self.mycolor):
    #         new_board = place_tetromino(board_dict, act, self.mycolor)
    #         self.children.append(BoardNode(new_board, self, act))
    #     return self.children
    def print_tree(self, level=0):
        print("Depth: ", level, " | Visited: ", self.visit, " | UCT: ", self.win, "/", self.win + self.loss + self.draw)
        if self.visit > 0:
            print(render_board(string_to_board(self.board_str), True))
        for child in self.children:
            child.print_tree(level + 1)