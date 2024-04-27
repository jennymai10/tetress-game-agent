import random
import math
from .boardnode import BoardNode
from .utils import string_to_board, generate_possible_moves, place_tetromino, render_board, game_over, winner
from referee.game import PlayerColor, Action, PlaceAction, Coord, Board

class MCTS:
    def __init__(self, root_board_dict: dict[Coord, PlayerColor], color: PlayerColor):
        self.root = BoardNode(root_board_dict, color)
        self.mycolor = color
        self.exploration_constant = 0.5

    def run(self, iterations: int) -> None:
        for _ in range(iterations):
            node = self.root
            while node.children:
                node = self.selection(node)
            self.expansion(node)
            playout = self.simulation(node)
            self.backpropagation(node, playout)
        self.root.print_tree()

    def selection(self, node: BoardNode) -> BoardNode:
        return max(node.children, key=lambda child: child.uct)

    def expansion(self, node: BoardNode) -> BoardNode:
        # Create a new child node for each possible move
        board_dict = string_to_board(node.board_str)
        print(render_board(board_dict, None, True))
        for move in generate_possible_moves(board_dict, self.mycolor):
            new_board = place_tetromino(board_dict, move, self.mycolor)
            new_node = BoardNode(new_board, self.mycolor, node, move)
            node.children.append(new_node)
        return random.choice(node.children)

    def simulation(self, node: BoardNode) -> PlayerColor | None:
        # Play a random playout from the new node to the end of the game
        board_dict = string_to_board(node.board_str)
        current_player = self.mycolor
        turn_num = 1
        while turn_num <= 150:
            possible_actions = generate_possible_moves(board_dict, current_player)
            if len(possible_actions) == 0 and current_player == PlayerColor.RED:
                # print("BLUE won")
                return PlayerColor.BLUE
            elif len(possible_actions) == 0 and current_player == PlayerColor.BLUE:
                # print("RED won")
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
        elif won == None:
            node.draw += 1
        else:
            node.loss += 1
        
        if node.parent is not None:
            node.uct = (node.win / node.visit) + (self.exploration_constant * math.sqrt(2 * math.log(node.parent.visit) / node.visit))
            self.backpropagation(node.parent, won)
        else:
            node.uct = (node.win / node.visit)