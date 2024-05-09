# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
import random
from .utils_rd import place_tetromino, generate_possible_moves, board_to_string, string_to_board, render_board

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
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def get_color(self) -> PlayerColor:
        return self.color
    def get_board(self) -> PlayerColor:
        return self.board
    
    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        if sum(1 for color in self.board.values() if color != None) == 0:
            return PlaceAction(Coord(5,4), Coord(5,5), Coord(5,6), Coord(4,5))
        if sum(1 for color in self.board.values() if color == self.color) == 0:
            return PlaceAction(Coord(2,1), Coord(2,2), Coord(2,3), Coord(1,2))
        return random.choice(generate_possible_moves(self.board, self.color))

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self.board = place_tetromino(self.board, action, color)