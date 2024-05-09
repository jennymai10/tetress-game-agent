from referee.game import PlayerColor, Coord, BOARD_N, Board
from agent.utils import render_board, place_tetromino, winner
from agent.mcts import MCTS
from agent.program import Agent as agent_mcts
from agent_mc_2.program_2 import Agent as agent_mcts_basic
from agent_random import Agent as agent_random
import cProfile

# target = None
# state = {}
# with open("test_csv/test-vis9.csv", "r") as file:
#     input = file.read()
# for r, line in enumerate(input.strip().split("\n")):
#     for c, p in enumerate(line.split(",")):
#         p = p.strip()
#         if line[0] != "#" and line.strip() != "" and p != "":
#             state[Coord(r, c)] = {
#                 "r": PlayerColor.RED,
#                 "b": PlayerColor.BLUE,
#             }[p.lower()]
#         if p == "B":
#             target = Coord(r, c)

# # Test the learning process of MC
# def play_game(board_dict: dict[Coord, PlayerColor], mycolor: PlayerColor):
#     mcts = MCTS(board_dict, mycolor, 25, 0.1)
#     best_child = mcts.selection(mcts.root)
#     print("Chosen move: ", best_child.uct, best_child.action)
#     print(render_board(string_to_board(best_child.board_str), ansi=True))

# if __name__ == '__main__':
#     c = play_game(state, PlayerColor.RED)
#     print("WINNER is: ", c)

def play_game(board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> PlayerColor | None:
    agent1 = agent_mcts(PlayerColor.BLUE)
    agent2 = agent_mcts_basic(PlayerColor.RED)

    current_player = agent2
    board_dict = {}
    for r in range(11):
        for c in range(11):
            board_dict[Coord(r, c)] = None
    turn_num = 1
    while turn_num <= 150:
        print("Turn: ", turn_num)
        turn = current_player.action()
        print(turn)
        board_dict = place_tetromino(board_dict, turn, current_player.get_color())
        print(current_player.get_color(), " turn:")
        print(render_board(board_dict, turn))
        agent1.update(current_player.get_color(), turn)
        agent2.update(current_player.get_color(), turn)
        turn_num = turn_num + 1
        if current_player == agent1:
            current_player = agent2
        else:
            current_player = agent1
    return winner(board_dict, current_player)

if __name__ == '__main__':
    c = play_game(None, PlayerColor.RED)
    # print("WINNER is: ", c)