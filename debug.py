from referee.game import PlayerColor, Coord, BOARD_N, Board
from agent_mc.utils import render_board, string_to_board, place_tetromino, winner
from agent_mc.mcts import MCTS
from agent_mc.program import Agent
from agent_random.program import Agent_Random


# Test the learning process of MC
# def play_game(board_dict: dict[Coord, PlayerColor], mycolor: PlayerColor):
#     mcts = MCTS(board_dict, mycolor)
#     mcts.run(25)
#     best_child = mcts.selection(mcts.root)
#     print("Chosen move: ", best_child.uct, best_child.action)
#     print(render_board(string_to_board(best_child.board_str), ansi=True))

def play_game(board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> PlayerColor | None:
    agent1 = Agent(PlayerColor.RED)
    agent2 = Agent(PlayerColor.BLUE)
    current_player = agent1
    board_dict = {}
    for r in range(11):
        for c in range(11):
            board_dict[Coord(r, c)] = None
    turn_num = 1
    while turn_num <= 150:
        turn = current_player.action()
        board_dict = place_tetromino(board_dict, turn, current_player.get_color())
        agent1.update(current_player.get_color(), turn)
        agent2.update(current_player.get_color(), turn)
        turn_num = turn_num + 1
        if current_player == agent1:
            current_player = agent2
        else:
            current_player = agent1
        print(current_player.get_color(), " turn:")
        print(render_board(board_dict))
    return (winner(board_dict, current_player))

# target = None
# state = {}
# with open("test_csv/test-vis1.csv", "r") as file:
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
c = play_game(None, PlayerColor.RED)