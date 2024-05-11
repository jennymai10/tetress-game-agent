# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import random
from referee.game import PlayerColor, Action, PlaceAction, Coord
from .utils import render_board, place_tetromino, generate_moves, random_first_move
from .mcts import MCTS
from .ending import Ending

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.color = color
        self.board = {}
        match color:
            case PlayerColor.RED:
                print("AGENT: I am playing as RED")
            case PlayerColor.BLUE:
                print("AGENT: I am playing as BLUE")

    def get_color(self) -> PlayerColor:
        return self.color

    def get_board(self):
        return self.board


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object.
        """
        # Modify how to choose first move
        cell_count = sum(1 for value in self.board.values() if value is not None)
        if cell_count == 0:
            if self.color == PlayerColor.RED:
                return random_first_move()
            else:
                mcts = MCTS(self.board, self.color, 10, 0.5)
                best_child = mcts.selection(mcts.root)
                action = best_child.action
                return action
        # if sum(1 for color in self.board.values() if color == self.color) == 0:
        #     return PlaceAction(Coord(2, 1), Coord(2, 2), Coord(2, 3), Coord(1, 2))

        # return random.choice(generate_possible_moves(self.board, self.color))
        print("Cell count: ", cell_count)
        if cell_count < 50:
            print("Decision by: Random")
            return random.choice(generate_moves(self.board, self.color))
        elif cell_count < 70:
            print("Decision by: MCTS")
            mcts = MCTS(self.board, self.color, 50, 0.5)
            best_child = mcts.selection(mcts.root)
            action = best_child.action
            return action
        else:
            print("Decision by: Ending")
            ending = Ending(self.board, self.color)
            ending_move = ending.generate_ending_move()
            return ending_move

    def update(self, color: PlayerColor, action: Action, **referee: dict) -> None:
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state.
        """
        self.board = place_tetromino(self.board, action, color)

