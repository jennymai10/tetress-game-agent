from referee.game import PlayerColor, Coord, PlaceAction
from .utils import generate_moves, place_tetromino, count_holes

class Ending:
    def __init__(self, root_board_dict: dict[Coord, PlayerColor], mycolor: PlayerColor):
        self.board = root_board_dict.copy()
        self.mycolor = mycolor

    def generate_ending_move(self) -> PlaceAction:
        my_possible_moves = generate_moves(self.board, self.mycolor)
        oppo_color = PlayerColor.RED if self.mycolor == PlayerColor.BLUE else PlayerColor.BLUE
        min_move = None
        min_oppo_possible_moves = float('inf')  # Initialize with positive infinity
        for move in my_possible_moves:
            new_board = place_tetromino(self.board, move, self.mycolor)
            oppo_possible_moves = generate_moves(new_board, oppo_color)
            if len(oppo_possible_moves) == 0:
                return move  # Found a move where opponent has no possible moves
            if len(oppo_possible_moves) < min_oppo_possible_moves or (
                    len(oppo_possible_moves) == min_oppo_possible_moves and count_holes(new_board) % 2 == 0):
                min_move = move
                min_oppo_possible_moves = len(oppo_possible_moves)
        return min_move
