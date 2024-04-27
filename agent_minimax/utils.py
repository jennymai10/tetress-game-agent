# Utility functions for the Minimax agent
from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N, board


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
    if color == "r":
        color_code = "\033[31m"
    if color == "b":
        color_code = "\033[34m"
    return f"{bold_code}{color_code}{text}\033[0m"


def render_board(
        board: dict[Coord, PlayerColor],
        target: Coord | None = None,
        ansi: bool = False
) -> str:
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
                is_target = target is not None and Coord(r, c) == target
                color = board[Coord(r, c)]
                color = "r" if color == PlayerColor.RED else "b"
                text = f"{color}" if not is_target else f"{color.upper()}"
                if ansi:
                    output += apply_ansi(text, color=color, bold=is_target)
                else:
                    output += text
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
    cell_content = board.get(coord)
    return cell_content is None


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

        # cell_value = board.get(new_coord)  # For debugging
        # print(f"Checking {new_coord}: {cell_value}, valid: {is_valid_cell(board, new_coord, target)}")

        if is_valid_cell(board, new_coord):
            neighbors.append(new_coord)
    return neighbors


def get_starting_cells(board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> list[Coord]:
    """
    Get the starting cells of my color
    """
    starting = []
    for cell in board:
        if board.get(cell) == mycolor:
            starting.append(cell)
    return starting


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


def is_valid_placement(positions: PlaceAction, board, mycolor: PlayerColor) -> bool:
    adjacent = []
    for cell in [positions.c1, positions.c2, positions.c3, positions.c4]:
        if board.get(cell) == PlayerColor.RED or board.get(cell) == PlayerColor.BLUE:
            return False
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_r = (cell.r + dr) % 11
            new_c = (cell.c + dc) % 11
            new_coord = Coord(new_r, new_c)
            adjacent.append(new_coord)
    for cell in adjacent:
        if board.get(cell) == mycolor:
            return True
    return False


def place_tetromino(board: dict[Coord, PlayerColor], action: PlaceAction, mycolor: PlayerColor) -> dict[
    Coord, PlayerColor]:
    '''Place the tetromino on the board and remove any filled lines'''
    new_board = board.copy()
    for pos in [action.c1, action.c2, action.c3, action.c4]:
        new_board[pos] = mycolor
    for row in range(11):
        filled_line = all(board.get(Coord(row, col)) is not None for col in range(11))
        if filled_line:
            for col in range(11):
                board[Coord(row, col)] = None

    for col in range(11):
        filled_line = all(board.get(Coord(row, col)) is not None for row in range(11))
        if filled_line:
            for row in range(11):
                board[Coord(row, col)] = None
    return new_board


def winner(board: dict[Coord, PlayerColor], turn: PlayerColor) -> PlayerColor | None:
    # l = generate_possible_moves(board, turn)
    # if len(l) == 0 and turn == PlayerColor.RED:
    #     return PlayerColor.BLUE
    # if len(l) == 0 and turn == PlayerColor.BLUE:
    #     return PlayerColor.RED
    red_count = sum(1 for color in board.values() if color == PlayerColor.RED)
    blue_count = sum(1 for color in board.values() if color == PlayerColor.BLUE)
    if red_count > blue_count:
        return PlayerColor.RED
    elif red_count < blue_count:
        return PlayerColor.BLUE
    else:
        return None


# def generate_possible_moves(mycolor: PlayerColor, current_board: dict[Coord, PlayerColor]):
#     shapes = get_all_tetromino_shapes()
#     moves = []
#     current_cells = get_starting_cells(current_board, mycolor)
#     available_neighbours = set()
#     for cell in current_cells:
#         available_neighbours.update(get_valid_neighbors(cell, current_board))
#     for shape in shapes:
#         for cell in available_neighbours:
#             move = PlaceAction(
#                 Coord((cell.r + shape[0][0]) % 11, (cell.c + shape[0][1]) % 11),
#                 Coord((cell.r + shape[1][0]) % 11, (cell.c + shape[1][1]) % 11),
#                 Coord((cell.r + shape[2][0]) % 11, (cell.c + shape[2][1]) % 11),
#                 Coord((cell.r + shape[3][0]) % 11, (cell.c + shape[3][1]) % 11)
#             )
#             if is_valid_placement(move, current_board, mycolor):
#                 moves.append(move)
#
#     return available_neighbours

def generate_possible_moves(board: dict[Coord, PlayerColor], color: PlayerColor) -> list[PlaceAction]:
    possible_moves = []
    all_tetrominoes = get_all_tetromino_shapes()
    states = set()

    for r in range(BOARD_N):
        for c in range(BOARD_N):
            cell = Coord(r, c)
            for tetro in all_tetrominoes:
                for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    c1 = Coord((cell.r + dx * tetro[0][0]) % 11, (cell.c + dy * tetro[0][1]) % 11)
                    c2 = Coord((cell.r + dx * tetro[1][0]) % 11, (cell.c + dy * tetro[1][1]) % 11)
                    c3 = Coord((cell.r + dx * tetro[2][0]) % 11, (cell.c + dy * tetro[2][1]) % 11)
                    c4 = Coord((cell.r + dx * tetro[3][0]) % 11, (cell.c + dy * tetro[3][1]) % 11)
                    action = PlaceAction(c1, c2, c3, c4)
                    if is_valid_placement(action, board, color):
                        new_board = place_tetromino(board, action, color)
                        new_state = board_to_string(new_board)
                        if new_state not in states:
                            states.add(new_state)
                            possible_moves.append(action)

    print(len(possible_moves), "possible moves")
    return possible_moves



def get_relative_positions(action: PlaceAction):
    """
    Get the relative positions of the coordinates in a PlaceAction.
    """
    base = action.c1
    pos = [(abs(coord.r - base.r), abs(coord.c - base.c)) for coord in [action.c1, action.c2, action.c3, action.c4]]
    return pos


def identify_shape(action: PlaceAction):
    """
    Identify the shape of a tetromino based on the PlaceAction coordinates.
    """
    # Define the relative positions of all tetromino shapes
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

    # Get the relative positions of the PlaceAction coordinates
    action_positions = get_relative_positions(action)

    # Compare with the defined shapes
    for shape, positions in tetrominoes.items():
        if action_positions in positions:
            return shape
    return None
