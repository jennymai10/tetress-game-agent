import time
import random
from referee.game import PlayerColor, Coord, BOARD_N, Board
from agent.utils import render_board, board_to_string, string_to_board, place_tetromino, winner, generate_possible_moves
from agent.mcts import MCTS

target = None
board = {}
with open("test_csv/test-vis2.csv", "r") as file:
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

possible_actions = generate_possible_moves(board, PlayerColor.BLUE)
print(len(possible_actions))
for move in possible_actions:
    b = place_tetromino(board, move, PlayerColor.BLUE)
    print(render_board(b))