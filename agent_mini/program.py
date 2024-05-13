from referee.game import PlayerColor, Action
from .minimax import MinimaxAgent
from .utils import place_tetromino, random_first_move
from .ending import Ending


class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        self.color = color
        self.board = {}
        self.agent = MinimaxAgent(color, self.board)
        match color:
            case PlayerColor.RED:
                print("MINIMAX: I am playing as RED")
            case PlayerColor.BLUE:
                print("MINIMAX: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        # make a random move
        cell_count = sum(1 for value in self.board.values() if value is not None)
        if cell_count == 0 or cell_count == 4:
            # frist move
            return random_first_move(self.color, self.board)
        
        cell_count = sum(1 for value in self.board.values() if value is not None)
        move = self.agent.select_move(self.board)
        
        if cell_count > 70:
            ending = Ending(self.board, self.color)
            move = ending.generate_ending_move()

        return move

    def update(self, color: PlayerColor, action: Action, **referee: dict) -> None:
        self.board = place_tetromino(self.board, action, color)
