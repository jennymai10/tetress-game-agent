class Node:
    def __init__(self, move, parent):
        self.move = move
        self.parent = parent
        self.children = {}
        self.win = 0
        self.playout = 0