from referee.game import PlayerColor, Action
from .minimax import MinimaxAgent
from .utils import place_tetromino, random_first_move


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
        if not self.board:
            return random_first_move(self.color)
        return self.agent.select_move(self.board)

    def update(self, color: PlayerColor, action: Action, **referee: dict) -> None:
        self.board = place_tetromino(self.board, action, color)
