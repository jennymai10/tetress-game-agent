import random
import math
from .boardnode import BoardNode
from .utils import generate_moves, place_tetromino, winner, heuristic_evaluation, string_to_board
from referee.game import PlayerColor, Coord


class MCTS:
    def __init__(self, root_board_dict: dict[Coord, PlayerColor], color: PlayerColor, iterations: int,
                 constant=math.sqrt(2)):
        self.root = BoardNode(root_board_dict, color)
        self.mycolor = color
        self.exploration_constant = constant
        self.iterations = iterations
        self.run(self.iterations)

    def run(self, iterations: int) -> None:
        for _ in range(iterations):
            node = self.root
            while node.children:
                node = self.selection(node)
            self.expansion(node)
            playout = self.simulation(node)
            self.backpropagation(node, playout)
        # self.root.print_tree()

    def selection(self, node: BoardNode) -> BoardNode:
        return max(node.children, key=lambda child: child.uct)

    def expansion(self, node: BoardNode) -> None:
        # Create a new child node for each possible move
        board_dict = string_to_board(node.board_str)
        moves = generate_moves(board_dict, self.mycolor)
        for move in moves:
            new_board = place_tetromino(board_dict, move, self.mycolor)
            new_node = BoardNode(new_board, self.mycolor, node, move)
            node.children.append(new_node)
        node.children.sort(key=lambda child: child.uct, reverse=True)
        node.children = node.children[:10]

    def simulation(self, node: BoardNode) -> PlayerColor | None:
        # Play a random playout from the new node to the end of the game
        board_dict = node.board.copy()
        current_player = self.mycolor
        turn_num = 1
        while turn_num <= 150:
            possible_actions = generate_moves(board_dict, current_player)
            if len(possible_actions) == 0 and current_player == PlayerColor.RED:
                return PlayerColor.BLUE
            elif len(possible_actions) == 0 and current_player == PlayerColor.BLUE:
                return PlayerColor.RED
            action = random.choice(possible_actions)
            board_dict = place_tetromino(board_dict, action, current_player)
            turn_num = turn_num + 1
            if current_player == PlayerColor.RED:
                current_player = PlayerColor.BLUE
            else:
                current_player = PlayerColor.RED
        return winner(board_dict, current_player)

    def backpropagation(self, node: BoardNode, won: PlayerColor | None) -> None:
        # Update the statistics of the nodes from the new node to the root
        node.visit += 1
        if won == self.mycolor:
            node.win += 1
        elif won is None:
            node.draw += 1
        else:
            node.loss += 1
        node.depth += 1
        # Check if the node is a leaf node (no children)
        if not node.children:
            node.uct = heuristic_evaluation(node.board, node.mycolor)
        elif node.parent is not None:
            node.uct = (node.win / node.visit) + (self.exploration_constant * math.sqrt(math.log(node.parent.visit) / node.visit)) + heuristic_evaluation(node.board, node.mycolor) * 0.5
            self.backpropagation(node.parent, won)
        else:
            node.uct = (node.win / node.visit)
