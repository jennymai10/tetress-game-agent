from referee.game import PlayerColor, Coord, BOARD_N, Board
from agent.utils import render_board, place_tetromino, winner
from agent.mcts import MCTS
from agent import Agent as agent_mcts
from agent_mini import Agent as agent_mini
from agent_random import Agent as agent_random
import cProfile

def play_game(board: dict[Coord, PlayerColor], mycolor: PlayerColor) -> PlayerColor | None:
    agent1 = agent_mcts(PlayerColor.BLUE)
    agent2 = agent_mini(PlayerColor.RED)

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
        board_dict = place_tetromino(board_dict, turn, current_player.color)
        print(current_player.__module__, " turn:")
        print(render_board(board_dict, turn))
        agent1.update(current_player.color, turn)
        agent2.update(current_player.color, turn)
        turn_num = turn_num + 1
        if current_player == agent1:
            current_player = agent2
        else:
            current_player = agent1
    return winner(board_dict, current_player)

if __name__ == '__main__':
    c = play_game(None, PlayerColor.RED)
    # print("WINNER is: ", c)