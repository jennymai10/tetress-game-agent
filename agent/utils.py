import random
import time

from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N, Board, IllegalActionException
from referee.game.pieces import PieceType, create_piece
from .disjointset import DisjointSet


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

    evaluation = (my_cell_count + 0.001) / (oppo_cell_count + 0.001) + holes_penalty
    return evaluation

 
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


def string_to_board(state: str) -> dict[Coord, PlayerColor]:
    """
    Convert a string state to board
    """
    board = {}
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            coord = Coord(r, c)
            if state[r * BOARD_N + c] == "1":
                board[coord] = PlayerColor.RED
            elif state[r * BOARD_N + c] == "2":
                board[coord] = PlayerColor.BLUE
    return board


def apply_ansi(text: str, bold: bool = True, color: str | None = None):
    """
    Wraps some text with ANSI control codes to apply terminal-based formatting.
    Note: Not all terminals will be compatible!
    """
    bold_code = "\033[1m" if bold else ""
    color_code = ""
    if color == "R":
        color_code = "\033[33m"
    elif color == "B":
        color_code = "\033[32m"
    elif color == "r":
        color_code = "\033[31m"
    elif color == "b":
        color_code = "\033[34m"
    return f"{bold_code}{color_code}{text}\033[0m"


def render_board(board: dict[Coord, PlayerColor], move: PlaceAction = None, ansi: bool = True) -> str:
    """
    Visualise the Tetress board via a multiline ASCII string, including
    optional ANSI styling for terminals that support this.

    If a target coordinate is provided, the token at that location will be
    capitalised/highlighted.
    """
    output = ""
    if board is None:
        return ("None")
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            if board.get(Coord(r, c), None):
                color = board[Coord(r, c)]
                if move and Coord(r, c) in move.coords and color == PlayerColor.RED:
                    color = "R"
                elif move and Coord(r, c) in move.coords and color == PlayerColor.BLUE:
                    color = "B"
                elif color == PlayerColor.RED:
                    color = "r"
                else:
                    color = "b"
                text = f"{color}"
                if ansi and (color == "R" or color == "B"):
                    output += apply_ansi(text, color=color, bold=True)
                else:
                    output += apply_ansi(text, color=color, bold=False)
            else:
                output += "."
            output += " "
        output += "\n"

    return output


def is_valid_cell(board: dict[Coord, PlayerColor], coord: Coord) -> bool:
    """
    Check if a cell is valid to place
    """
    # If coord is not empty to place
    return board.get(coord) is None


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


def get_starting_cells(board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> list[Coord]:
    """
    Get the starting cells of my color
    """
    return [cell for cell in board.keys() if board[cell] == mycolor]


def get_all_tetromino_shapes():
    # Define all tetromino shapes in their fixed orientations
    tetrominoes = {
        'I': [[(0, 0), (1, 0), (2, 0), (3, 0)],
              [(0, 0), (0, 1), (0, 2), (0, 3)]],
        'O': [[(0, 0), (0, 1), (1, 0), (1, 1)]],
        'T': [[(0, 0), (1, 0), (2, 0), (1, 1)],
              [(0, 1), (1, 0), (1, 1), (1, 2)],
              [(1, 0), (0, 1), (1, 1), (2, 1)],
              [(1, 0), (0, 1), (1, 1), (1, 2)]],
        'J': [[(0, 0), (1, 0), (2, 0), (2, 1)],
              [(0, 0), (0, 1), (1, 1), (2, 1)],
              [(0, 0), (0, 1), (1, 0), (2, 0)],
              [(0, 0), (1, 0), (0, 1), (0, 2)]],
        'L': [[(0, 1), (1, 1), (2, 0), (2, 1)],
              [(0, 0), (1, 0), (2, 0), (0, 1)],
              [(0, 0), (0, 1), (1, 0), (2, 0)],
              [(2, 0), (0, 1), (1, 1), (2, 1)]],
        'S': [[(0, 1), (1, 0), (1, 1), (2, 0)],
              [(0, 0), (0, 1), (1, 1), (1, 2)]],
        'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)],
              [(1, 0), (0, 1), (1, 1), (0, 2)]]
    }

    all_shapes = [shape for shapes in tetrominoes.values() for shape in shapes]
    return all_shapes


def is_valid_placement(positions: PlaceAction, board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> bool:
    adjacent = set()
    for cell in [positions.c1, positions.c2, positions.c3, positions.c4]:
        if board.get(cell) is not None:
            return False
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_r = (cell.r + dr) % 11
            new_c = (cell.c + dc) % 11
            new_coord = Coord(new_r, new_c)
            adjacent.add(new_coord)
    return any(board.get(cell) == mycolor for cell in adjacent)


def place_tetromino(board: dict[Coord, PlayerColor], action: PlaceAction, mycolor: PlayerColor) -> dict[
    Coord, PlayerColor]:
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


def get_valid_neighbors_list(coords: list[Coord], board: dict[Coord, PlayerColor], board_size: int = 11) -> list[Coord]:
    neighbors = []
    for coord in coords:
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            # Adjust row and column values for toroidal wrap-around
            new_r = (coord.r + dr) % board_size
            new_c = (coord.c + dc) % board_size
            new_coord = Coord(new_r, new_c)
            if board.get(new_coord) is None:
                neighbors.append(new_coord)
    return neighbors

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

def generate_possible_moves(board: dict[Coord, PlayerColor], color: PlayerColor) -> list[PlaceAction]:
    board_dict = board.copy()

    my_cells = get_starting_cells(board_dict, color)
    my_neighbors = get_valid_neighbors_list(my_cells, board_dict)
    actions = []
    for neighbor in my_neighbors:
        for i in generate_pieces_for_position(board_dict, neighbor):
            if i not in actions:
                actions.append(i)
    return actions


def generate_pieces_for_position(board: dict[Coord, PlayerColor], cell: Coord) -> list[PlaceAction]:
    """
    Given a cell coordinate and a board state, return all legal piece (tetromino) arrangements for that 
    cell in a list.
    Each piece will have a maximum of 4 arrangements, since there is a possibility that all 4 cells of
    the piece itself can be placed on the given cell.
    """
    pieces = []
    pieces.extend(generate_I_pieces(board, cell))
    pieces.extend(generate_L_pieces(board, cell))
    pieces.extend(generate_J_pieces(board, cell))
    pieces.extend(generate_T_pieces(board, cell))
    pieces.extend(generate_Z_pieces(board, cell))
    pieces.extend(generate_S_pieces(board, cell))
    pieces.extend(generate_O_pieces(board, cell))
    return pieces


def generate_I_pieces(
        board: dict[Coord, PlayerColor],
        cell: Coord
) -> list[PlaceAction]:
    """
    Given a cell coordinate and a board state, return all legal I piece (tetromino) arrangements for that 
    cell in a list.
    Each piece will have a maximum of 4 arrangements, since there is a possibility that all 4 cells of
    the piece itself can be placed on the given cell.
    """
    I_pieces = []

    # Horizontal I piece
    if (piece_is_legal(board, PlaceAction(cell, cell.right(), cell.right(2), cell.right(3)))):
        I_pieces.append(PlaceAction(cell, cell.right(), cell.right(2), cell.right(3)))
    if (piece_is_legal(board, PlaceAction(cell.left(), cell, cell.right(), cell.right(2)))):
        I_pieces.append(PlaceAction(cell.left(), cell, cell.right(), cell.right(2)))
    if (piece_is_legal(board, PlaceAction(cell.left(2), cell.left(), cell, cell.right()))):
        I_pieces.append(PlaceAction(cell.left(2), cell.left(), cell, cell.right()))
    if (piece_is_legal(board, PlaceAction(cell.left(3), cell.left(2), cell.left(), cell))):
        I_pieces.append(PlaceAction(cell.left(3), cell.left(2), cell.left(), cell))
    # Vertical I piece
    if (piece_is_legal(board, PlaceAction(cell, cell.down(), cell.down(2), cell.down(3)))):
        I_pieces.append(PlaceAction(cell, cell.down(), cell.down(2), cell.down(3)))
    if (piece_is_legal(board, PlaceAction(cell.up(), cell, cell.down(), cell.down(2)))):
        I_pieces.append(PlaceAction(cell.up(), cell, cell.down(), cell.down(2)))
    if (piece_is_legal(board, PlaceAction(cell.up(2), cell.up(), cell, cell.down()))):
        I_pieces.append(PlaceAction(cell.up(2), cell.up(), cell, cell.down()))
    if (piece_is_legal(board, PlaceAction(cell.up(3), cell.up(2), cell.up(), cell))):
        I_pieces.append(PlaceAction(cell.up(3), cell.up(2), cell.up(), cell))

    return I_pieces


def generate_L_pieces(
        board: dict[Coord, PlayerColor],
        cell: Coord
) -> list[PlaceAction]:
    """
    Given a cell coordinate and a board state, return all legal L piece (tetromino) arrangements for that 
    cell in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 cells of
    the piece itself can be placed on the given cell.
    """
    L_pieces = []

    # L piece rotated 0 degrees to the right
    if piece_is_legal(board, PlaceAction(cell, cell.down(), cell.down(2), cell.down(2).right())):
        L_pieces.append(PlaceAction(cell, cell.down(), cell.down(2), cell.down(2).right()))
    if piece_is_legal(board, PlaceAction(cell.up(), cell, cell.down(), cell.down().right())):
        L_pieces.append(PlaceAction(cell.up(), cell, cell.down(), cell.down().right()))
    if piece_is_legal(board, PlaceAction(cell.up(2), cell.up(), cell, cell.right())):
        L_pieces.append(PlaceAction(cell.up(2), cell.up(), cell, cell.right()))
    if piece_is_legal(board, PlaceAction(cell.left().up(2), cell.left().up(), cell.left(), cell)):
        L_pieces.append(PlaceAction(cell.left().up(2), cell.left().up(), cell.left(), cell))
    # L piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.left(), cell.left(2), cell.left(2).down()))):
        L_pieces.append(PlaceAction(cell, cell.left(), cell.left(2), cell.left(2).down()))
    if (piece_is_legal(board, PlaceAction(cell.right(), cell, cell.left(), cell.left().down()))):
        L_pieces.append(PlaceAction(cell.right(), cell, cell.left(), cell.left().down()))
    if (piece_is_legal(board, PlaceAction(cell.right(2), cell.right(), cell, cell.down()))):
        L_pieces.append(PlaceAction(cell.right(2), cell.right(), cell, cell.down()))
    if (piece_is_legal(board, PlaceAction(cell.up().right(2), cell.up().right(), cell.up(), cell))):
        L_pieces.append(PlaceAction(cell.up().right(2), cell.up().right(), cell.up(), cell))
    # L piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.up(), cell.up(2), cell.up(2).left()))):
        L_pieces.append(PlaceAction(cell, cell.up(), cell.up(2), cell.up(2).left()))
    if (piece_is_legal(board, PlaceAction(cell.down(), cell, cell.up(), cell.up().left()))):
        L_pieces.append(PlaceAction(cell.down(), cell, cell.up(), cell.up().left()))
    if (piece_is_legal(board, PlaceAction(cell.down(2), cell.down(), cell, cell.left()))):
        L_pieces.append(PlaceAction(cell.down(2), cell.down(), cell, cell.left()))
    if (piece_is_legal(board, PlaceAction(cell.right().down(2), cell.right().down(), cell.right(), cell))):
        L_pieces.append(PlaceAction(cell.right().down(2), cell.right().down(), cell.right(), cell))
    # L piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.right(), cell.right(2), cell.right(2).up()))):
        L_pieces.append(PlaceAction(cell, cell.right(), cell.right(2), cell.right(2).up()))
    if (piece_is_legal(board, PlaceAction(cell.left(), cell, cell.right(), cell.right().up()))):
        L_pieces.append(PlaceAction(cell.left(), cell, cell.right(), cell.right().up()))
    if (piece_is_legal(board, PlaceAction(cell.left(2), cell.left(), cell, cell.up()))):
        L_pieces.append(PlaceAction(cell.left(2), cell.left(), cell, cell.up()))
    if (piece_is_legal(board, PlaceAction(cell.down().left(2), cell.down().left(), cell.down(), cell))):
        L_pieces.append(PlaceAction(cell.down().left(2), cell.down().left(), cell.down(), cell))
    return L_pieces


def generate_J_pieces(
        board: dict[Coord, PlayerColor],
        cell: Coord
) -> list[PlaceAction]:
    """
    Given a cell coordinate and a board state, return all legal J piece (tetromino) arrangements for that 
    cell in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 cells of
    the piece itself can be placed on the given cell.
    """
    J_pieces = []

    # J piece rotated 0 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.down(), cell.down(2), cell.down(2).left()))):
        J_pieces.append(PlaceAction(cell, cell.down(), cell.down(2), cell.down(2).left()))
    if (piece_is_legal(board, PlaceAction(cell.up(), cell, cell.down(), cell.down().left()))):
        J_pieces.append(PlaceAction(cell.up(), cell, cell.down(), cell.down().left()))
    if (piece_is_legal(board, PlaceAction(cell.up(2), cell.up(), cell, cell.left()))):
        J_pieces.append(PlaceAction(cell.up(2), cell.up(), cell, cell.left()))
    if (piece_is_legal(board, PlaceAction(cell.right().up(2), cell.right().up(), cell.right(), cell))):
        J_pieces.append(PlaceAction(cell.right().up(2), cell.right().up(), cell.right(), cell))
    # J piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.left(), cell.left(2), cell.left(2).up()))):
        J_pieces.append(PlaceAction(cell, cell.left(), cell.left(2), cell.left(2).up()))
    if (piece_is_legal(board, PlaceAction(cell.right(), cell, cell.left(), cell.left().up()))):
        J_pieces.append(PlaceAction(cell.right(), cell, cell.left(), cell.left().up()))
    if (piece_is_legal(board, PlaceAction(cell.right(2), cell.right(), cell, cell.up()))):
        J_pieces.append(PlaceAction(cell.right(2), cell.right(), cell, cell.up()))
    if (piece_is_legal(board, PlaceAction(cell.down().right(2), cell.down().right(), cell.down(), cell))):
        J_pieces.append(PlaceAction(cell.down().right(2), cell.down().right(), cell.down(), cell))
    # J piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.up(), cell.up(2), cell.up(2).right()))):
        J_pieces.append(PlaceAction(cell, cell.up(), cell.up(2), cell.up(2).right()))
    if (piece_is_legal(board, PlaceAction(cell.down(), cell, cell.up(), cell.up().right()))):
        J_pieces.append(PlaceAction(cell.down(), cell, cell.up(), cell.up().right()))
    if (piece_is_legal(board, PlaceAction(cell.down(2), cell.down(), cell, cell.right()))):
        J_pieces.append(PlaceAction(cell.down(2), cell.down(), cell, cell.right()))
    if (piece_is_legal(board, PlaceAction(cell.left().down(2), cell.left().down(), cell.left(), cell))):
        J_pieces.append(PlaceAction(cell.left().down(2), cell.left().down(), cell.left(), cell))
    # J piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.right(), cell.right(2), cell.right(2).down()))):
        J_pieces.append(PlaceAction(cell, cell.right(), cell.right(2), cell.right(2).down()))
    if (piece_is_legal(board, PlaceAction(cell.left(), cell, cell.right(), cell.right().down()))):
        J_pieces.append(PlaceAction(cell.left(), cell, cell.right(), cell.right().down()))
    if (piece_is_legal(board, PlaceAction(cell.left(2), cell.left(), cell, cell.down()))):
        J_pieces.append(PlaceAction(cell.left(2), cell.left(), cell, cell.down()))
    if (piece_is_legal(board, PlaceAction(cell.up().left(2), cell.up().left(), cell.up(), cell))):
        J_pieces.append(PlaceAction(cell.up().left(2), cell.up().left(), cell.up(), cell))

    return J_pieces


def generate_T_pieces(
        board: dict[Coord, PlayerColor],
        cell: Coord
) -> list[PlaceAction]:
    """
    Given a cell coordinate and a board state, return all legal T piece (tetromino) arrangements for that 
    cell in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 cells of
    the piece itself can be placed on the given cell.
    """
    T_pieces = []

    # T piece rotated 0 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.right(), cell.right().down(), cell.right(2)))):
        T_pieces.append(PlaceAction(cell, cell.right(), cell.right().down(), cell.right(2)))
    if (piece_is_legal(board, PlaceAction(cell.left(), cell, cell.down(), cell.right()))):
        T_pieces.append(PlaceAction(cell.left(), cell, cell.down(), cell.right()))
    if (piece_is_legal(board, PlaceAction(cell.left().up(), cell.up(), cell, cell.right().up()))):
        T_pieces.append(PlaceAction(cell.left().up(), cell.up(), cell, cell.right().up()))
    if (piece_is_legal(board, PlaceAction(cell.left(2), cell.left(), cell.down().left(), cell))):
        T_pieces.append(PlaceAction(cell.left(2), cell.left(), cell.down().left(), cell))
    # T piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.down(), cell.down().left(), cell.down(2)))):
        T_pieces.append(PlaceAction(cell, cell.down(), cell.down().left(), cell.down(2)))
    if (piece_is_legal(board, PlaceAction(cell.up(), cell, cell.left(), cell.down()))):
        T_pieces.append(PlaceAction(cell.up(), cell, cell.left(), cell.down()))
    if (piece_is_legal(board, PlaceAction(cell.up().right(), cell.right(), cell, cell.down().right()))):
        T_pieces.append(PlaceAction(cell.up().right(), cell.right(), cell, cell.down().right()))
    if (piece_is_legal(board, PlaceAction(cell.up(2), cell.up(), cell.left().up(), cell))):
        T_pieces.append(PlaceAction(cell.up(2), cell.up(), cell.left().up(), cell))
    # T piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.left(), cell.left().up(), cell.left(2)))):
        T_pieces.append(PlaceAction(cell, cell.left(), cell.left().up(), cell.left(2)))
    if (piece_is_legal(board, PlaceAction(cell.right(), cell, cell.up(), cell.left()))):
        T_pieces.append(PlaceAction(cell.right(), cell, cell.up(), cell.left()))
    if (piece_is_legal(board, PlaceAction(cell.right().down(), cell.down(), cell, cell.left().down()))):
        T_pieces.append(PlaceAction(cell.right().down(), cell.down(), cell, cell.left().down()))
    if (piece_is_legal(board, PlaceAction(cell.right(2), cell.right(), cell.up().right(), cell))):
        T_pieces.append(PlaceAction(cell.right(2), cell.right(), cell.up().right(), cell))
    # T piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.up(), cell.up().right(), cell.up(2)))):
        T_pieces.append(PlaceAction(cell, cell.up(), cell.up().right(), cell.up(2)))
    if (piece_is_legal(board, PlaceAction(cell.down(), cell, cell.right(), cell.up()))):
        T_pieces.append(PlaceAction(cell.down(), cell, cell.right(), cell.up()))
    if (piece_is_legal(board, PlaceAction(cell.down().left(), cell.left(), cell, cell.up().left()))):
        T_pieces.append(PlaceAction(cell.down().left(), cell.left(), cell, cell.up().left()))
    if (piece_is_legal(board, PlaceAction(cell.down(2), cell.down(), cell.right().down(), cell))):
        T_pieces.append(PlaceAction(cell.down(2), cell.down(), cell.right().down(), cell))

    return T_pieces


def generate_Z_pieces(
        board: dict[Coord, PlayerColor],
        cell: Coord
) -> list[PlaceAction]:
    """
    Given a cell coordinate and a board state, return all legal Z piece (tetromino) arrangements for that 
    cell in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 cells of
    the piece itself can be placed on the given cell.
    """
    Z_pieces = []

    # Z piece rotated 0/180 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.right(), cell.right().down(), cell.right(2).down()))):
        Z_pieces.append(PlaceAction(cell, cell.right(), cell.right().down(), cell.right(2).down()))
    if (piece_is_legal(board, PlaceAction(cell.left(), cell, cell.down(), cell.right().down()))):
        Z_pieces.append(PlaceAction(cell.left(), cell, cell.down(), cell.right().down()))
    if (piece_is_legal(board, PlaceAction(cell.left().up(), cell.up(), cell, cell.right()))):
        Z_pieces.append(PlaceAction(cell.left().up(), cell.up(), cell, cell.right()))
    if (piece_is_legal(board, PlaceAction(cell.left(2).up(), cell.left().up(), cell.left(), cell))):
        Z_pieces.append(PlaceAction(cell.left(2).up(), cell.left().up(), cell.left(), cell))
    # Z piece rotated 90/270 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.down(), cell.down().left(), cell.down(2).left()))):
        Z_pieces.append(PlaceAction(cell, cell.down(), cell.down().left(), cell.down(2).left()))
    if (piece_is_legal(board, PlaceAction(cell.up(), cell, cell.left(), cell.down().left()))):
        Z_pieces.append(PlaceAction(cell.up(), cell, cell.left(), cell.down().left()))
    if (piece_is_legal(board, PlaceAction(cell.up().right(), cell.right(), cell, cell.down()))):
        Z_pieces.append(PlaceAction(cell.up().right(), cell.right(), cell, cell.down()))
    if (piece_is_legal(board, PlaceAction(cell.up(2).right(), cell.up().right(), cell.up(), cell))):
        Z_pieces.append(PlaceAction(cell.up(2).right(), cell.up().right(), cell.up(), cell))

    return Z_pieces


def generate_S_pieces(
        board: dict[Coord, PlayerColor],
        cell: Coord
) -> list[PlaceAction]:
    """
    Given a cell coordinate and a board state, return all legal S piece (tetromino) arrangements for that 
    cell in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 cells of
    the piece itself can be placed on the given cell.
    """
    S_pieces = []

    # S piece rotated 0/180 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.right(), cell.right().up(), cell.right(2).up()))):
        S_pieces.append(PlaceAction(cell, cell.right(), cell.right().up(), cell.right(2).up()))
    if (piece_is_legal(board, PlaceAction(cell.left(), cell, cell.up(), cell.right().up()))):
        S_pieces.append(PlaceAction(cell.left(), cell, cell.up(), cell.right().up()))
    if (piece_is_legal(board, PlaceAction(cell.left().down(), cell.down(), cell, cell.right()))):
        S_pieces.append(PlaceAction(cell.left().down(), cell.down(), cell, cell.right()))
    if (piece_is_legal(board, PlaceAction(cell.left(2).down(), cell.left().down(), cell.left(), cell))):
        S_pieces.append(PlaceAction(cell.left(2).down(), cell.left().down(), cell.left(), cell))
    # S piece rotated 90/270 degrees to the right
    if (piece_is_legal(board, PlaceAction(cell, cell.down(), cell.down().right(), cell.down(2).right()))):
        S_pieces.append(PlaceAction(cell, cell.down(), cell.down().right(), cell.down(2).right()))
    if (piece_is_legal(board, PlaceAction(cell.up(), cell, cell.right(), cell.down().right()))):
        S_pieces.append(PlaceAction(cell.up(), cell, cell.right(), cell.down().right()))
    if (piece_is_legal(board, PlaceAction(cell.up().left(), cell.left(), cell, cell.down()))):
        S_pieces.append(PlaceAction(cell.up().left(), cell.left(), cell, cell.down()))
    if (piece_is_legal(board, PlaceAction(cell.up(2).left(), cell.up().left(), cell.up(), cell))):
        S_pieces.append(PlaceAction(cell.up(2).left(), cell.up().left(), cell.up(), cell))

    return S_pieces


def generate_O_pieces(
        board: dict[Coord, PlayerColor],
        cell: Coord
) -> list[PlaceAction]:
    """
    Given a cell coordinate and a board state, return all legal O piece (tetromino) arrangements for that 
    cell in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 cells of
    the piece itself can be placed on the given cell.
    """
    O_pieces = []

    if (piece_is_legal(board, PlaceAction(cell, cell.right(), cell.down(), cell.right().down()))):
        O_pieces.append(PlaceAction(cell, cell.right(), cell.down(), cell.right().down()))
    if (piece_is_legal(board, PlaceAction(cell, cell.left(), cell.down(), cell.left().down()))):
        O_pieces.append(PlaceAction(cell, cell.left(), cell.down(), cell.left().down()))
    if (piece_is_legal(board, PlaceAction(cell, cell.right(), cell.up(), cell.right().up()))):
        O_pieces.append(PlaceAction(cell, cell.right(), cell.up(), cell.right().up()))
    if (piece_is_legal(board, PlaceAction(cell, cell.left(), cell.up(), cell.left().up()))):
        O_pieces.append(PlaceAction(cell, cell.left(), cell.up(), cell.left().up()))

    return O_pieces


def piece_is_legal(
        board: dict[Coord, PlayerColor],
        piece: PlaceAction
) -> bool:
    """
    Given a PlaceAction with 4 coordinates and a board state, return true if none of the 4 coordinates already 
    exist in the board state dict, false otherwise. Essentially checking if the PlaceAction is a legal move.
    """
    if piece.c1 in board:
        return False
    if piece.c2 in board:
        return False
    if piece.c3 in board:
        return False
    if piece.c4 in board:
        return False

    return True


