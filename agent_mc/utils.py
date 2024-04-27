from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N

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
        color_code = "\033[31m"
    if color == "B":
        color_code = "\033[34m"
    return f"{bold_code}{color_code}{text}\033[0m"

def render_board(board: dict[Coord, PlayerColor], ansi: bool = False) -> str:
    """
    Visualise the Tetress board via a multiline ASCII string, including
    optional ANSI styling for terminals that support this.

    If a target coordinate is provided, the token at that location will be
    capitalised/highlighted.
    """
    output = ""
    if board is None:
        return("None")
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            if board.get(Coord(r, c), None):
                color = board[Coord(r, c)]
                color = "R" if color == PlayerColor.RED else "B"
                text = f"{color}"
                if ansi:
                    output += apply_ansi(text, color=color, bold=True)
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
        'I': [ [(0, 0), (1, 0), (2, 0), (3, 0)],
               [(0, 0), (0, 1), (0, 2), (0, 3)] ],
        'O': [ [(0, 0), (0, 1), (1, 0), (1, 1)] ],
        'T': [ [(0, 0), (1, 0), (2, 0), (1, 1)],
               [(0, 1), (1, 0), (1, 1), (1, 2)],
               [(1, 0), (0, 1), (1, 1), (2, 1)],
               [(1, 0), (0, 1), (1, 1), (1, 2)] ],
        'J': [ [(0, 0), (1, 0), (2, 0), (2, 1)],
               [(0, 0), (0, 1), (1, 1), (2, 1)],
               [(0, 0), (0, 1), (1, 0), (2, 0)],
               [(0, 0), (1, 0), (0, 1), (0, 2)] ],
        'L': [ [(0, 1), (1, 1), (2, 0), (2, 1)],
               [(0, 0), (1, 0), (2, 0), (0, 1)],
               [(0, 0), (0, 1), (1, 0), (2, 0)],
               [(2, 0), (0, 1), (1, 1), (2, 1)] ],
        'S': [ [(0, 1), (1, 0), (1, 1), (2, 0)],
               [(0, 0), (0, 1), (1, 1), (1, 2)] ],
        'Z': [ [(0, 0), (1, 0), (1, 1), (2, 1)],
               [(1, 0), (0, 1), (1, 1), (0, 2)] ]
    }

    all_shapes = [shape for shapes in tetrominoes.values() for shape in shapes]
    return all_shapes

def generate_possible_moves(board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> list[PlaceAction]:
    possible_moves = []
    all_tetrominoes = get_all_tetromino_shapes()
    starting_cells = get_starting_cells(board, mycolor)
    neighbors = []
    states = set()

    for cell in starting_cells:
        neighbors.append(get_valid_neighbors(cell, board, 11))

    for neigh in neighbors:
        for _ , tetro in enumerate(all_tetrominoes):

            for n in neigh:
                c1 = Coord((n.r + tetro[0][0]) % 11, (n.c + tetro[0][1]) % 11)
                c2 = Coord((n.r + tetro[1][0]) % 11, (n.c + tetro[1][1]) % 11)
                c3 = Coord((n.r + tetro[2][0]) % 11, (n.c + tetro[2][1]) % 11)
                c4 = Coord((n.r + tetro[3][0]) % 11, (n.c + tetro[3][1]) % 11)
                action = PlaceAction(c1, c2, c3, c4)
                if is_valid_placement(action, board, mycolor):
                    new_board = place_tetromino(board, action, mycolor)
                    board_str = board_to_string(new_board)
                    if board_str not in states:
                        states.add(board_str)
                        possible_moves.append(action)
                c1 = Coord((n.r + tetro[0][0]) % 11, (n.c - tetro[0][1]) % 11)
                c2 = Coord((n.r + tetro[1][0]) % 11, (n.c - tetro[1][1]) % 11)
                c3 = Coord((n.r + tetro[2][0]) % 11, (n.c - tetro[2][1]) % 11)
                c4 = Coord((n.r + tetro[3][0]) % 11, (n.c - tetro[3][1]) % 11)
                action = PlaceAction(c1, c2, c3, c4)
                if is_valid_placement(action, board, mycolor):
                    new_board = place_tetromino(board, action, mycolor)
                    board_str = board_to_string(new_board)
                    if board_str not in states:
                        states.add(board_str)
                        possible_moves.append(action)
                c1 = Coord((n.r - tetro[0][0]) % 11, (n.c + tetro[0][1]) % 11)
                c2 = Coord((n.r - tetro[1][0]) % 11, (n.c + tetro[1][1]) % 11)
                c3 = Coord((n.r - tetro[2][0]) % 11, (n.c + tetro[2][1]) % 11)
                c4 = Coord((n.r - tetro[3][0]) % 11, (n.c + tetro[3][1]) % 11)
                action = PlaceAction(c1, c2, c3, c4)
                if is_valid_placement(action, board, mycolor):
                    new_board = place_tetromino(board, action, mycolor)
                    board_str = board_to_string(new_board)
                    if board_str not in states:
                        states.add(board_str)
                        possible_moves.append(action)
                c1 = Coord((n.r - tetro[0][0]) % 11, (n.c - tetro[0][1]) % 11)
                c2 = Coord((n.r - tetro[1][0]) % 11, (n.c - tetro[1][1]) % 11)
                c3 = Coord((n.r - tetro[2][0]) % 11, (n.c - tetro[2][1]) % 11)
                c4 = Coord((n.r - tetro[3][0]) % 11, (n.c - tetro[3][1]) % 11)
                action = PlaceAction(c1, c2, c3, c4)
                if is_valid_placement(action, board, mycolor):
                    new_board = place_tetromino(board, action, mycolor)
                    board_str = board_to_string(new_board)
                    if board_str not in states:
                        states.add(board_str)
                        possible_moves.append(action)
    return possible_moves

        
def is_valid_placement(positions: PlaceAction, board, mycolor: PlayerColor) -> bool:
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

def place_tetromino(board: dict[Coord, PlayerColor], action: PlaceAction, mycolor: PlayerColor) -> dict[Coord, PlayerColor]:
    new_board = board.copy()
    for pos in [action.c1, action.c2, action.c3, action.c4]:
        new_board[pos] = mycolor
    rows_to_clear = set()
    cols_to_clear = set()
    for row in range(11):
        if all(new_board.get(Coord(row, col)) is not None for col in range(11)):
            rows_to_clear.add(row)
    for col in range(11):
        if all(new_board.get(Coord(row, col)) is not None for row in range(11)):
            cols_to_clear.add(col)
    for row in rows_to_clear:
        for col in range(11):
            new_board[Coord(row, col)] = None
    for col in cols_to_clear:
        for row in range(11):
            new_board[Coord(row, col)] = None
    return new_board

# def game_over(board: dict[Coord, PlayerColor]) -> bool:
#     l1 = generate_possible_moves(board, PlayerColor.RED)
#     l2 = generate_possible_moves(board, PlayerColor.BLUE)
#     return len(l1) == 0 and len(l2) == 0

def winner(board: dict[Coord, PlayerColor], turn: PlayerColor) -> PlayerColor | None:
    red_count = sum(1 for color in board.values() if color == PlayerColor.RED)
    blue_count = sum(1 for color in board.values() if color == PlayerColor.BLUE)
    if red_count > blue_count:
        return PlayerColor.RED
    elif red_count < blue_count:
        return PlayerColor.BLUE
    else:
        return None