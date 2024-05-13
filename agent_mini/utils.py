import random
import time

from .disjointset import DisjointSet
from referee.game import Coord, PlaceAction, PlayerColor, IllegalActionException, BOARD_N
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

def board_to_string(board: dict[Coord, PlayerColor]) -> str:
    """
    Convert the board to a string state
    """
    state = ""
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            if board.get(Coord(r, c), None) == PlayerColor.RED:
                state += "1"
            elif board.get(Coord(r, c), None) == PlayerColor.BLUE:
                state += "2"
            else:
                state += "0"
    return state

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

def valid_first_move(board, move, color) -> bool:
    for coord in [move.c1, move.c2, move.c3, move.c4]:
        if not is_valid_cell(board, coord):
            return False
        return True


def random_first_move(color, board: dict[Coord, PlayerColor]) -> PlaceAction:
    # preferred = PlaceAction(Coord(0, 0), Coord(0, 10), Coord(10, 0), Coord(10, 10))
    all_cells = [Coord(r, c) for r in range(11) for c in range(11)]
    middle_cells = [Coord(5, 4), Coord(4, 5), Coord(5, 6), Coord(6, 5)]

    temp = board.copy()
    if color is PlayerColor.RED:
        choosen =  random.choice(middle_cells)
        temp[choosen] = PlayerColor.RED
        available_moves = generate_moves(temp, PlayerColor.RED)
        move_score = []
        for move in available_moves:
            temp_board = place_tetromino(temp, move, PlayerColor.RED)
            move_score.append((move, heuristic_evaluation(temp_board, PlayerColor.RED)))
        # get highest score move
        move = max(move_score, key=lambda x: x[1])[0]
        return move
    
    if color is PlayerColor.BLUE:
        # Find unoccupied cells
        occupied = board.keys()
        
        unoccupied_cells = list(set(all_cells) - set(occupied))
        
        # Randomly select one of the unoccupied cells
        selected_cell = random.choice(unoccupied_cells)
        # change the color of the cell
        temp[selected_cell] = PlayerColor.BLUE
        available_moves = generate_moves(temp, PlayerColor.BLUE)
        move_score = []
        for move in available_moves:
            temp_board = place_tetromino(temp, move, PlayerColor.BLUE)
            move_score.append((move, heuristic_evaluation(temp_board, PlayerColor.BLUE)))
        # get highest score move
        move = max(move_score, key=lambda x: x[1])[0]
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

    holes_penalty = 0
    if sum(1 for value in board_dict.values() if value is not None) > 80:
        holes_count = count_holes(board_dict)
        if holes_count % 2 != 0:
            holes_penalty = -1
        else:
            holes_penalty = 1

    # Load the winning boards from a file
    with open('winning_board.txt', 'r') as f:
        winning_boards = [line.strip() for line in f]

    # Convert the current board to a string
    board_string = board_to_string(board_dict)

    # Check if the current board matches any of the winning boards
    if board_string in winning_boards:
        return float('inf')

    # Continue with your existing heuristic evaluation...
    evaluation = (my_cell_count + 0.001) / (oppo_cell_count + 0.001) + holes_penalty
    return evaluation
