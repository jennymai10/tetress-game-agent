from referee.game import PlayerColor

'''
Assign a value for each tetromino piece based on placeability and potential
line removals. Range from 0 to 1
'''
o_shape_value = 0.4 # medium low value
i_shape_value = 0.9 # highest value
t_shape_value = 0.6 # medium value
j_shape_value = 0.7 # medium high value
l_shape_value = 0.7 # medium high value
z_shape_value = 0.3 # low value
s_shape_value = 0.3 # low value

def evaluate(currentPlayer):
    '''
    Evaluate the current board state
    '''
    evalRed = countMaterial(PlayerColor.RED)
    evalBlue = countMaterial(PlayerColor.BLUE)

    eval = evalRed - evalBlue
    # 1 for red turn to move, -1 for blue turn to move
    if currentPlayer == PlayerColor.RED:
        return eval
    else:
        return -eval

def countMaterial(PlayerColor):
    totalScore = 0
    

    pass

def miniMaxSearch(depth):
    pass


