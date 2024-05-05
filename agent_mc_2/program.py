# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from .utils import render_board, string_to_board, place_tetromino, generate_possible_moves
from .mcts import MCTS

class Agent_MC_2:
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
        for r in range(11):
            for c in range(11):
                self.board[Coord(r, c)] = None
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
        
        mcts = MCTS(self.board, self.color, 10, 0.5)

        best_child = mcts.selection(mcts.root)
        action = best_child.action
        return action

    def update(self, color: PlayerColor, action: Action, **referee: dict) -> None:
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        self.board = place_tetromino(self.board, action, color)