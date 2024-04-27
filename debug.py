from referee.game import PlayerColor, Coord, BOARD_N, Board
from agent_mc.utils import render_board, string_to_board, place_tetromino
from agent_mc.mcts import MCTS

# Test the learning process of MC
def play_game(board_dict: dict[Coord, PlayerColor], mycolor: PlayerColor):
    mcts = MCTS(board_dict, mycolor)
    mcts.run(25)
    best_child = mcts.selection(mcts.root)
    print("Chosen move: ", best_child.uct, best_child.action)
    print(render_board(string_to_board(best_child.board_str), ansi=True))

# Load test-vis1.csv board
target = None
state = {}
with open("test_csv/test-vis1.csv", "r") as file:
    input = file.read()
for r, line in enumerate(input.strip().split("\n")):
    for c, p in enumerate(line.split(",")):
        p = p.strip()
        if line[0] != "#" and line.strip() != "" and p != "":
            state[Coord(r, c)] = {
                "r": PlayerColor.RED,
                "b": PlayerColor.BLUE,
            }[p.lower()]
        if p == "B":
            target = Coord(r, c)
play_game(state, PlayerColor.RED)