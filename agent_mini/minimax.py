from .utils import generate_moves, place_tetromino, winner, heuristic_evaluation, board_to_string
import json


class MinimaxNode:
    def __init__(self, board, move, color):
        self.board = board
        self.move = move
        self.color = color

class MinimaxAgent:
    def __init__(self, color, board):
        self.color = color
        self.board = board

    # def select_move(self, board):
    #     best_move = None
    #     best_value = -float('inf')

    #     for move in generate_moves(board, self.color):
    #         new_board = place_tetromino(board, move, self.color)
    #         node = MinimaxNode(new_board, move, self.color)
    #         value = self.minimax(node, 500, -float('inf'), float('inf'), True)

    #         try:
    #             with open('winning_board.txt', 'r') as f:
    #                 winning_board = f.read()
    #         except FileNotFoundError:
    #                 winning_board = None
    #         if board_to_string(new_board) in winning_board:
    #             return move
            
    #         if value > best_value:
    #             best_value = value
    #             best_move = move
        
    #     if winner(board, self.color) is not None:
    #         with open("winning_board.txt", "a") as f:
    #             f.write(f"{board_to_string(board)}\n")

    #     return best_move
    def select_move(self, board):
        best_move = None
        best_value = -float('inf')

        for move in generate_moves(board, self.color):
            new_board = place_tetromino(board, move, self.color)
            node = MinimaxNode(new_board, move, self.color)
            value = self.minimax(node, 500, -float('inf'), float('inf'), True)

            if value > best_value:
                best_value = value
                best_move = move

        # If the game is won, save the final board state
        final_board = place_tetromino(board, best_move, self.color)
        if winner(final_board, self.color) is not None:
            with open('winning_board.txt', 'a') as f:
                f.write(f"{board_to_string(final_board)}\n")

        return best_move

    def minimax(self, node, depth, alpha, beta, maximizing_player):
        if depth == 0 or winner(node.board, node.color) is not None:
            return self.evaluate(node.board)

        if maximizing_player:
            max_eval = -float('inf')
            for move in generate_moves(node.board, self.color):
                new_board = place_tetromino(node.board, move, self.color)
                child_node = MinimaxNode(new_board, move, self.color)
                evaluation = self.minimax(child_node, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in generate_moves(node.board, self.color):
                new_board = place_tetromino(node.board, move, self.color)
                child_node = MinimaxNode(new_board, move, self.color)
                evaluation = self.minimax(child_node, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate(self, board):
        return heuristic_evaluation(board, self.color)

