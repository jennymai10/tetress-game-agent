import time
import random
from referee.game import PlayerColor, Coord, PlaceAction
from agent_mc.utils import render_board, count_holes, generate_possible_moves, place_tetromino
from agent_mc.mcts import MCTS
from agent_mc.ending import Ending

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

# mcts = MCTS(board, PlayerColor.BLUE, 15, 0.01)
# best_child = mcts.selection(mcts.root)
# print("Chosen move: ", best_child.uct, best_child.action)
# print(render_board(best_child.board, best_child.action))

# action = generate_possible_moves(board, PlayerColor.BLUE)
# for a in action:
#     new_board = place_tetromino(board, a, PlayerColor.BLUE)
#     print(render_board(board, a))
# print(render_board(board))

ending = Ending(board, PlayerColor.BLUE)
ending_move = ending.generate_ending_move()
new_board = place_tetromino(board, ending_move, PlayerColor.BLUE)
print(render_board(new_board, ending_move))
print(render_board(new_board))

# test_board = place_tetromino(board, PlaceAction(Coord(0,4), Coord(0,5), Coord(1,5), Coord(2,5)), PlayerColor.BLUE)
# print(render_board(test_board, PlaceAction(Coord(0,4), Coord(0,5), Coord(1,5), Coord(2,5))))