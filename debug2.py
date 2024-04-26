# import time
# import random
# from referee.game import PlayerColor, Coord, BOARD_N, Board
# from agent.utils import render_board, board_to_string, string_to_board, place_tetromino, winner, generate_possible_moves
# from agent.mcts import MCTS

# target = None
# board = {}
# with open("test_csv/test-vis1.csv", "r") as file:
#     input = file.read()
# for r, line in enumerate(input.strip().split("\n")):
#     for c, p in enumerate(line.split(",")):
#         p = p.strip()
#         if line[0] != "#" and line.strip() != "" and p != "":
#             board[Coord(r, c)] = {
#                 "r": PlayerColor.RED,
#                 "b": PlayerColor.BLUE,
#             }[p.lower()]
#         if p == "B":
#             target = Coord(r, c)

# current_player = PlayerColor.RED # start with red goes first
# turn_num = 1
# while turn_num <= 150:
#     print("Turn of: ", current_player)
#     possible_actions = generate_possible_moves(board, current_player)
#     if len(possible_actions) == 0 and current_player == PlayerColor.RED:
#         print("BLUE won")
#         break
#     elif len(possible_actions) == 0 and current_player == PlayerColor.BLUE:
#         print("RED won")
#         break
#     action = random.choice(possible_actions)
#     board = place_tetromino(board, action, current_player)
#     turn_num = turn_num + 1
#     if current_player == PlayerColor.RED:
#         current_player = PlayerColor.BLUE
#     else:
#         current_player = PlayerColor.RED
#     print(current_player)
#     print(render_board(board, None, ansi=True))
# # print(winner(board, current_player))