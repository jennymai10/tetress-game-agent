import time
import random
from referee.game import PlayerColor, Coord, BOARD_N, Board
from agent.utils import render_board, count_holes
from agent.mcts import MCTS

target = None
board = {}
with open("test_csv/test-vis9.csv", "r") as file:
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

holes = count_holes(board)
print(holes)