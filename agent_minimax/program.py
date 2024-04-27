# Program entry point for minimax agent
from referee.game import PlayerColor, Action, PlaceAction, Coord
from agent.utils import place_tetromino


class AgentMiniMax:

    def __init__(self, myColor: PlayerColor, **referee: dict):
        self.color = myColor
        self.board = {}
        for r in range(11):
            for c in range(11):
                self.board[Coord(r, c)] = None
        match myColor:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        match self.color:
            case PlayerColor.RED:
                print("Testing: RED is playing a PLACE action")
                return PlaceAction(
                    Coord(3, 3),
                    Coord(3, 4),
                    Coord(4, 3),
                    Coord(4, 4)
                )
            case PlayerColor.BLUE:
                print("Testing: BLUE is playing a PLACE action")
                return PlaceAction(
                    Coord(2, 3),
                    Coord(2, 4),
                    Coord(2, 5),
                    Coord(2, 6)
                )

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        self.board = place_tetromino(self.board, action, color)
