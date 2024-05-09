import time
import random
from referee.game import PlayerColor, Coord, BOARD_N, Board
from agent.utils import render_board, count_holes
from agent.mcts import MCTS

target = None
board = {}
with open("test_csv/test-vis1.csv", "r") as file:
    input = file.read()
for r, line in enumerate(input.strip().split("\n")):
    for c, p in enumerate(line.split(",")):
        p = p.strip()
        if line[0] != "#" and line.strip() != "" and p != "":
            board[Coord(r, c)] = {
                "r": PlayerColor.RED,
                "b": PlayerColor.BLUE,
            }[p.lower()]
        if p == "B":
            target = Coord(r, c)
print(render_board(board))

mcts = MCTS(board, PlayerColor.BLUE, 15, 0.01)
best_child = mcts.selection(mcts.root)
print("Chosen move: ", best_child.uct, best_child.action)
print(render_board(best_child.board, best_child.action))