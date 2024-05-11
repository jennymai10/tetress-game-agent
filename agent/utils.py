import random
import time

from .disjointset import DisjointSet
from referee.game import Coord, PlaceAction, PlayerColor, IllegalActionException
from referee.game.pieces import PieceType, create_piece


def get_valid_neighbors(coord: Coord, board: dict[Coord, PlayerColor], board_size: int = 11) -> list[Coord]:
    """
    Get the neighbors of a given coordinate on a toroidal board.
    """
    neighbors = []
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        # Adjust row and column values for toroidal wrap-around
        new_r = (coord.r + dr) % board_size
        new_c = (coord.c + dc) % board_size
        new_coord = Coord(new_r, new_c)
        if is_valid_cell(board, new_coord):
            neighbors.append(new_coord)
    return neighbors


def is_valid_cell(board: dict[Coord, PlayerColor], coord: Coord) -> bool:
    """
    Check if a cell is valid to place
    """
    # If coord is not empty to place
    return board.get(coord) is None


def get_starting_cells(board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> list[Coord]:
    """
    Get the starting cells of my color
    """
    return [cell for cell in board.keys() if board[cell] == mycolor]


def place_tetromino(board: dict[Coord, PlayerColor], action: PlaceAction, mycolor: PlayerColor) \
        -> dict[Coord, PlayerColor]:
    new_board = board.copy()
    for pos in [action.c1, action.c2, action.c3, action.c4]:
        new_board[pos] = mycolor
    to_delete = []
    for row in range(11):
        filled_line = all(new_board.get(Coord(row, col)) is not None for col in range(11))
        if filled_line:
            for col in range(11):
                to_delete.append(Coord(row, col))

    for col in range(11):
        filled_line = all(new_board.get(Coord(row, col)) is not None for row in range(11))
        if filled_line:
            for row in range(11):
                to_delete.append(Coord(row, col))
    for cell in to_delete:
        if new_board.get(cell) is not None:
            new_board.pop(cell)
    return new_board


def winner(board: dict[Coord, PlayerColor], turn: PlayerColor) -> PlayerColor | None:
    red_count = sum(1 for color in board.values() if color == PlayerColor.RED)
    blue_count = sum(1 for color in board.values() if color == PlayerColor.BLUE)
    if red_count > blue_count:
        return PlayerColor.RED
    elif red_count < blue_count:
        return PlayerColor.BLUE
    else:
        return None


def generate_moves(board: dict[Coord, PlayerColor], color: PlayerColor) -> list[PlaceAction]:
    """
    Given a board state and a color, return a list of all possible moves for that color.
    """
    # get all empty cell

    occupied = set(board.keys())

    # for cells that is not in occupied try place a piece
    moves = []
    for r in range(11):
        for c in range(11):
            if Coord(r, c) not in occupied:
                for piece_type in PieceType:
                    piece = create_piece(piece_type, Coord(r, c))
                    move = PlaceAction(*piece.coords)
                    if move_is_legal(board, move, color):
                        moves.append(move)
    # print(len(moves), 'possible moves')
    return moves


def move_is_legal(board: dict[Coord, PlayerColor], move: PlaceAction, color: PlayerColor) -> bool:
    # Check if all four coordinates on the board are unoccupied
    if any(coord in board for coord in [move.c1, move.c2, move.c3, move.c4]):
        return False

    # Check if at least one coordinate is directly adjacent to an already-placed token of the same color
    # This check is skipped if it is the player's first action of the game
    has_neighbour = False
    for coord in [move.c1, move.c2, move.c3, move.c4]:
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            # Adjust row and column values for toroidal wrap-around
            new_r = (coord.r + dr) % 11
            new_c = (coord.c + dc) % 11
            new_coord = Coord(new_r, new_c)
            if board.get(new_coord) == color:
                has_neighbour = True
                break
        if has_neighbour:
            break
    if not has_neighbour:
        return False

    return True


def random_first_move() -> PlaceAction:
    # Randomly place a piece on the board
    # Randomly select a piece type
    piece_type = random.choice(list(PieceType))
    random.seed(time.time() + 99999)
    # Randomly select a cell to place the piece within the centre 4x4 grid to assert dominance
    try:
        cell = Coord(random.randint(4, 6), random.randint(4, 6))
        piece = create_piece(piece_type, cell)
        move = PlaceAction(*piece.coords)
    except IllegalActionException:
        random.seed(time.time())
        cell = Coord(random.randint(0, 10), random.randint(0, 10))
        piece = create_piece(piece_type, cell)
        move = PlaceAction(*piece.coords)
    return move


def count_holes(board: dict[Coord, PlayerColor]) -> int:
    disjoint_set = DisjointSet()
    parent = []
    for r in range(11):
        for c in range(11):
            if board.get(Coord(r, c)) is None:
                disjoint_set.make_set(Coord(r, c))
                parent.append(Coord(r, c))
    for coord in parent:
        neighbors = get_valid_neighbors(coord, board)
        for neighbor in neighbors:
            disjoint_set.union(coord, neighbor)

    num_disjoint_sets = 0
    set_sizes = {}
    for coord in parent:
        parent_coord = disjoint_set.find_set(coord)
        if parent_coord in set_sizes:
            set_sizes[parent_coord] += 1
        else:
            set_sizes[parent_coord] = 1

    for size in set_sizes.values():
        if size >= 4:
            num_disjoint_sets += 1

    return num_disjoint_sets


def heuristic_evaluation(board_dict: dict[Coord, PlayerColor], mycolor: PlayerColor) -> float:
    """
    Evaluate the quality of each possible action based on the current game state using heuristics.
    Higher values indicate more favorable actions.
    """
    oppo_color = PlayerColor.RED if mycolor == PlayerColor.BLUE else PlayerColor.BLUE
    oppo_cell_count = len(get_starting_cells(board_dict, oppo_color))
    my_cell_count = len(get_starting_cells(board_dict, mycolor))

    # Favor clearing opponent's cells without losing too much our cell

    # Penalize odd number of holes
    holes_penalty = 0
    if sum(1 for value in board_dict.values() if value is not None) > 80:
        holes_count = count_holes(board_dict)
        if holes_count % 2 == 0:
            holes_penalty = -1
        else:
            holes_penalty = 1

    # Favor the middle of the board
    center = Coord(5, 5)
    distance_penalty = 0
    for coord, color in board_dict.items():
        if color == mycolor:
            distance_penalty -= ((coord.r - center.r) ** 2 + (coord.c - center.c) ** 2)

    evaluation = (my_cell_count + 0.001) / (oppo_cell_count + 0.001) + holes_penalty + distance_penalty
    return evaluation

# def heuristic_evaluation(board_dict: dict[Coord, PlayerColor], mycolor: PlayerColor) -> float:
#     """
#     Evaluate the quality of each possible action based on the current game state using heuristics.
#     Higher values indicate more favorable actions.
#     """
#     best_evaluation = float('-inf')
#
#     oppo_color = PlayerColor.RED if mycolor == PlayerColor.BLUE else PlayerColor.BLUE
#     oppo_cell_count_before = len(get_starting_cells(board_dict, oppo_color))
#     my_cell_count = len(get_starting_cells(board_dict, mycolor))
#
#     # Generate all possible moves
#     possible_moves = generate_moves(board_dict, mycolor)
#
#     for action in possible_moves:
#         # Simulate the move
#         new_board = place_tetromino(board_dict, action, mycolor)
#         oppo_cell_count_after = len(get_starting_cells(new_board, oppo_color))
#
#         # Calculate the number of opponent cells that would be cleared by the move
#         clear_bonus = oppo_cell_count_before - oppo_cell_count_after
#
#         # Other heuristics remain the same
#         holes_penalty = 0
#         if sum(1 for value in board_dict.values() if value is not None) > 80:
#             holes_count = count_holes(board_dict)
#             if holes_count % 2 == 0:
#                 holes_penalty = -1
#             else:
#                 holes_penalty = 1
#
#         # Favor the middle of the board
#         center = Coord(5, 5)
#         distance_penalty = 0
#         for coord, color in board_dict.items():
#             if color == mycolor:
#                 dr = min(abs(coord.r - center.r), 11 - abs(coord.r - center.r))
#                 dc = min(abs(coord.c - center.c), 11 - abs(coord.c - center.c))
#                 distance_penalty -= (dr ** 2 + dc ** 2)
#
#         evaluation = (my_cell_count + 0.001) / (
#                     oppo_cell_count_after + 0.001) + holes_penalty + distance_penalty + clear_bonus
#         best_evaluation = max(best_evaluation, evaluation)
#
#     return best_evaluation
