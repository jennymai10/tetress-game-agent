from referee.game import Coord, PlaceAction, PlayerColor, BOARD_N


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


def is_valid_cell(board: dict[Coord, PlayerColor], coord: Coord) -> bool:
    """
    Check if a cell is valid to place
    """
    # If coord is not empty to place
    cell_content = board.get(coord)
    return cell_content is None


def get_starting_cells(board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> list[Coord]:
    """
    Get the starting cells of my color
    """
    starting = []
    for cell in board:
        if board.get(cell) == mycolor:
            starting.append(cell)
    return starting


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


def generate_pieces_for_square(
        board: dict[Coord, PlayerColor],
        square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have a maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    pieces = []
    pieces.extend(generate_I_pieces(board, square))
    pieces.extend(generate_L_pieces(board, square))
    pieces.extend(generate_J_pieces(board, square))
    pieces.extend(generate_T_pieces(board, square))
    pieces.extend(generate_Z_pieces(board, square))
    pieces.extend(generate_S_pieces(board, square))
    pieces.extend(generate_O_pieces(board, square))
    return pieces


def generate_I_pieces(
        board: dict[Coord, PlayerColor],
        square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal I piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have a maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    I_pieces = []

    # Horizontal I piece
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right(2), square.right(3)))):
        I_pieces.append(PlaceAction(square, square.right(), square.right(2), square.right(3)))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.right(), square.right(2)))):
        I_pieces.append(PlaceAction(square.left(), square, square.right(), square.right(2)))
    if (piece_is_legal(board, PlaceAction(square.left(2), square.left(), square, square.right()))):
        I_pieces.append(PlaceAction(square.left(2), square.left(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left(3), square.left(2), square.left(), square))):
        I_pieces.append(PlaceAction(square.left(3), square.left(2), square.left(), square))
    # Vertical I piece
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down(2), square.down(3)))):
        I_pieces.append(PlaceAction(square, square.down(), square.down(2), square.down(3)))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.down(), square.down(2)))):
        I_pieces.append(PlaceAction(square.up(), square, square.down(), square.down(2)))
    if (piece_is_legal(board, PlaceAction(square.up(2), square.up(), square, square.down()))):
        I_pieces.append(PlaceAction(square.up(2), square.up(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up(3), square.up(2), square.up(), square))):
        I_pieces.append(PlaceAction(square.up(3), square.up(2), square.up(), square))

    return I_pieces;


def generate_L_pieces(
        board: dict[Coord, PlayerColor],
        square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal L piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    L_pieces = []

    # L piece rotated 0 degrees to the right
    if piece_is_legal(board, PlaceAction(square, square.down(), square.down(2), square.down(2).right())):
        L_pieces.append(PlaceAction(square, square.down(), square.down(2), square.down(2).right()))
    if piece_is_legal(board, PlaceAction(square.up(), square, square.down(), square.down().right())):
        L_pieces.append(PlaceAction(square.up(), square, square.down(), square.down().right()))
    if piece_is_legal(board, PlaceAction(square.up(2), square.up(), square, square.right())):
        L_pieces.append(PlaceAction(square.up(2), square.up(), square, square.right()))
    if piece_is_legal(board, PlaceAction(square.left().up(2), square.left().up(), square.left(), square)):
        L_pieces.append(PlaceAction(square.left().up(2), square.left().up(), square.left(), square))
    # L piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.left(2), square.left(2).down()))):
        L_pieces.append(PlaceAction(square, square.left(), square.left(2), square.left(2).down()))
    if (piece_is_legal(board, PlaceAction(square.right(), square, square.left(), square.left().down()))):
        L_pieces.append(PlaceAction(square.right(), square, square.left(), square.left().down()))
    if (piece_is_legal(board, PlaceAction(square.right(2), square.right(), square, square.down()))):
        L_pieces.append(PlaceAction(square.right(2), square.right(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up().right(2), square.up().right(), square.up(), square))):
        L_pieces.append(PlaceAction(square.up().right(2), square.up().right(), square.up(), square))
    # L piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.up(), square.up(2), square.up(2).left()))):
        L_pieces.append(PlaceAction(square, square.up(), square.up(2), square.up(2).left()))
    if (piece_is_legal(board, PlaceAction(square.down(), square, square.up(), square.up().left()))):
        L_pieces.append(PlaceAction(square.down(), square, square.up(), square.up().left()))
    if (piece_is_legal(board, PlaceAction(square.down(2), square.down(), square, square.left()))):
        L_pieces.append(PlaceAction(square.down(2), square.down(), square, square.left()))
    if (piece_is_legal(board, PlaceAction(square.right().down(2), square.right().down(), square.right(), square))):
        L_pieces.append(PlaceAction(square.right().down(2), square.right().down(), square.right(), square))
    # L piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right(2), square.right(2).up()))):
        L_pieces.append(PlaceAction(square, square.right(), square.right(2), square.right(2).up()))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.right(), square.right().up()))):
        L_pieces.append(PlaceAction(square.left(), square, square.right(), square.right().up()))
    if (piece_is_legal(board, PlaceAction(square.left(2), square.left(), square, square.up()))):
        L_pieces.append(PlaceAction(square.left(2), square.left(), square, square.up()))
    if (piece_is_legal(board, PlaceAction(square.down().left(2), square.down().left(), square.down(), square))):
        L_pieces.append(PlaceAction(square.down().left(2), square.down().left(), square.down(), square))

    return L_pieces


def generate_J_pieces(
        board: dict[Coord, PlayerColor],
        square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal J piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    J_pieces = []

    # J piece rotated 0 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down(2), square.down(2).left()))):
        J_pieces.append(PlaceAction(square, square.down(), square.down(2), square.down(2).left()))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.down(), square.down().left()))):
        J_pieces.append(PlaceAction(square.up(), square, square.down(), square.down().left()))
    if (piece_is_legal(board, PlaceAction(square.up(2), square.up(), square, square.left()))):
        J_pieces.append(PlaceAction(square.up(2), square.up(), square, square.left()))
    if (piece_is_legal(board, PlaceAction(square.right().up(2), square.right().up(), square.right(), square))):
        J_pieces.append(PlaceAction(square.right().up(2), square.right().up(), square.right(), square))
    # J piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.left(2), square.left(2).up()))):
        J_pieces.append(PlaceAction(square, square.left(), square.left(2), square.left(2).up()))
    if (piece_is_legal(board, PlaceAction(square.right(), square, square.left(), square.left().up()))):
        J_pieces.append(PlaceAction(square.right(), square, square.left(), square.left().up()))
    if (piece_is_legal(board, PlaceAction(square.right(2), square.right(), square, square.up()))):
        J_pieces.append(PlaceAction(square.right(2), square.right(), square, square.up()))
    if (piece_is_legal(board, PlaceAction(square.down().right(2), square.down().right(), square.down(), square))):
        J_pieces.append(PlaceAction(square.down().right(2), square.down().right(), square.down(), square))
    # J piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.up(), square.up(2), square.up(2).right()))):
        J_pieces.append(PlaceAction(square, square.up(), square.up(2), square.up(2).right()))
    if (piece_is_legal(board, PlaceAction(square.down(), square, square.up(), square.up().right()))):
        J_pieces.append(PlaceAction(square.down(), square, square.up(), square.up().right()))
    if (piece_is_legal(board, PlaceAction(square.down(2), square.down(), square, square.right()))):
        J_pieces.append(PlaceAction(square.down(2), square.down(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left().down(2), square.left().down(), square.left(), square))):
        J_pieces.append(PlaceAction(square.left().down(2), square.left().down(), square.left(), square))
    # J piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right(2), square.right(2).down()))):
        J_pieces.append(PlaceAction(square, square.right(), square.right(2), square.right(2).down()))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.right(), square.right().down()))):
        J_pieces.append(PlaceAction(square.left(), square, square.right(), square.right().down()))
    if (piece_is_legal(board, PlaceAction(square.left(2), square.left(), square, square.down()))):
        J_pieces.append(PlaceAction(square.left(2), square.left(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up().left(2), square.up().left(), square.up(), square))):
        J_pieces.append(PlaceAction(square.up().left(2), square.up().left(), square.up(), square))

    return J_pieces


def generate_T_pieces(
        board: dict[Coord, PlayerColor],
        square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal T piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    T_pieces = []

    # T piece rotated 0 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right().down(), square.right(2)))):
        T_pieces.append(PlaceAction(square, square.right(), square.right().down(), square.right(2)))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.down(), square.right()))):
        T_pieces.append(PlaceAction(square.left(), square, square.down(), square.right()))
    if (piece_is_legal(board, PlaceAction(square.left().up(), square.up(), square, square.right().up()))):
        T_pieces.append(PlaceAction(square.left().up(), square.up(), square, square.right().up()))
    if (piece_is_legal(board, PlaceAction(square.left(2), square.left(), square.down().left(), square))):
        T_pieces.append(PlaceAction(square.left(2), square.left(), square.down().left(), square))
    # T piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down().left(), square.down(2)))):
        T_pieces.append(PlaceAction(square, square.down(), square.down().left(), square.down(2)))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.left(), square.down()))):
        T_pieces.append(PlaceAction(square.up(), square, square.left(), square.down()))
    if (piece_is_legal(board, PlaceAction(square.up().right(), square.right(), square, square.down().right()))):
        T_pieces.append(PlaceAction(square.up().right(), square.right(), square, square.down().right()))
    if (piece_is_legal(board, PlaceAction(square.up(2), square.up(), square.left().up(), square))):
        T_pieces.append(PlaceAction(square.up(2), square.up(), square.left().up(), square))
    # T piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.left().up(), square.left(2)))):
        T_pieces.append(PlaceAction(square, square.left(), square.left().up(), square.left(2)))
    if (piece_is_legal(board, PlaceAction(square.right(), square, square.up(), square.left()))):
        T_pieces.append(PlaceAction(square.right(), square, square.up(), square.left()))
    if (piece_is_legal(board, PlaceAction(square.right().down(), square.down(), square, square.left().down()))):
        T_pieces.append(PlaceAction(square.right().down(), square.down(), square, square.left().down()))
    if (piece_is_legal(board, PlaceAction(square.right(2), square.right(), square.up().right(), square))):
        T_pieces.append(PlaceAction(square.right(2), square.right(), square.up().right(), square))
    # T piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.up(), square.up().right(), square.up(2)))):
        T_pieces.append(PlaceAction(square, square.up(), square.up().right(), square.up(2)))
    if (piece_is_legal(board, PlaceAction(square.down(), square, square.right(), square.up()))):
        T_pieces.append(PlaceAction(square.down(), square, square.right(), square.up()))
    if (piece_is_legal(board, PlaceAction(square.down().left(), square.left(), square, square.up().left()))):
        T_pieces.append(PlaceAction(square.down().left(), square.left(), square, square.up().left()))
    if (piece_is_legal(board, PlaceAction(square.down(2), square.down(), square.right().down(), square))):
        T_pieces.append(PlaceAction(square.down(2), square.down(), square.right().down(), square))

    return T_pieces


def generate_Z_pieces(
        board: dict[Coord, PlayerColor],
        square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal Z piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    Z_pieces = []

    # Z piece rotated 0/180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right().down(), square.right(2).down()))):
        Z_pieces.append(PlaceAction(square, square.right(), square.right().down(), square.right(2).down()))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.down(), square.right().down()))):
        Z_pieces.append(PlaceAction(square.left(), square, square.down(), square.right().down()))
    if (piece_is_legal(board, PlaceAction(square.left().up(), square.up(), square, square.right()))):
        Z_pieces.append(PlaceAction(square.left().up(), square.up(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left(2).up(), square.left().up(), square.left(), square))):
        Z_pieces.append(PlaceAction(square.left(2).up(), square.left().up(), square.left(), square))
    # Z piece rotated 90/270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down().left(), square.down(2).left()))):
        Z_pieces.append(PlaceAction(square, square.down(), square.down().left(), square.down(2).left()))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.left(), square.down().left()))):
        Z_pieces.append(PlaceAction(square.up(), square, square.left(), square.down().left()))
    if (piece_is_legal(board, PlaceAction(square.up().right(), square.right(), square, square.down()))):
        Z_pieces.append(PlaceAction(square.up().right(), square.right(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up(2).right(), square.up().right(), square.up(), square))):
        Z_pieces.append(PlaceAction(square.up(2).right(), square.up().right(), square.up(), square))

    return Z_pieces


def generate_S_pieces(
        board: dict[Coord, PlayerColor],
        square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal S piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    S_pieces = []

    # S piece rotated 0/180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right().up(), square.right(2).up()))):
        S_pieces.append(PlaceAction(square, square.right(), square.right().up(), square.right(2).up()))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.up(), square.right().up()))):
        S_pieces.append(PlaceAction(square.left(), square, square.up(), square.right().up()))
    if (piece_is_legal(board, PlaceAction(square.left().down(), square.down(), square, square.right()))):
        S_pieces.append(PlaceAction(square.left().down(), square.down(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left(2).down(), square.left().down(), square.left(), square))):
        S_pieces.append(PlaceAction(square.left(2).down(), square.left().down(), square.left(), square))
    # S piece rotated 90/270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down().right(), square.down(2).right()))):
        S_pieces.append(PlaceAction(square, square.down(), square.down().right(), square.down(2).right()))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.right(), square.down().right()))):
        S_pieces.append(PlaceAction(square.up(), square, square.right(), square.down().right()))
    if (piece_is_legal(board, PlaceAction(square.up().left(), square.left(), square, square.down()))):
        S_pieces.append(PlaceAction(square.up().left(), square.left(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up(2).left(), square.up().left(), square.up(), square))):
        S_pieces.append(PlaceAction(square.up(2).left(), square.up().left(), square.up(), square))

    return S_pieces


def generate_O_pieces(
        board: dict[Coord, PlayerColor],
        square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal O piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    O_pieces = []

    if (piece_is_legal(board, PlaceAction(square, square.right(), square.down(), square.right().down()))):
        O_pieces.append(PlaceAction(square, square.right(), square.down(), square.right().down()))
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.down(), square.left().down()))):
        O_pieces.append(PlaceAction(square, square.left(), square.down(), square.left().down()))
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.up(), square.right().up()))):
        O_pieces.append(PlaceAction(square, square.right(), square.up(), square.right().up()))
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.up(), square.left().up()))):
        O_pieces.append(PlaceAction(square, square.left(), square.up(), square.left().up()))

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

    return True;
