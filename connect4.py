import numpy as np
import pygame
import sys
import math
import copy

# Followed the python tutorial https://www.askpython.com/python/examples/connect-four-game
# Followed MCTS implementation https://github.com/Alfo5123/Connect4/blob/master/README.md

ROW_COUNT = 6
COLUMN_COUNT = 7
# MCTS CONFIG
MCTS_MAX_ITER = 3000
MCTS_FACTOR = 2.0
# MINMAX CONFIG
MINMAX_DEPTH = 4
DEFAULT_ALPHA = -9999999
DEFAULT_BETA = 9999999

# I cannot explain what this is for, only that Alfredo de la Fuente refers to it in her/his is_winner method
dx = [1, 1,  1,  0]
dy = [1, 0,  -1,  1]

# Pygame GUI RGB colors and time
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WAIT_TIME = 10000

# Python dictionary to map integers (1, -1, 0) to characters ('x', 'o', ' ')
# Used only for console version
symbols = { 1:'x',
           -1:'o',
            0:' '}



### CONNECT4 BOARD CLASS
class C4(object):

    def __init__(self):
        # A 6x7 2D array containing tokens and game states
        self.board = np.zeros((ROW_COUNT, COLUMN_COUNT))
        # Records the last move attempted
        self.last_move = [None, None]



    # Place a token in a selected column with row already computed
    def place_token(self, row, col, player):
        self.board[row][col] = player



    # Find the first available row (starting from the bottom)
    def get_next_open_row(self, col):
        if (col < 0 or col >= COLUMN_COUNT or self.board[0][col] != 0 ):
            return -1;
        
        for r in range(ROW_COUNT-1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return ROW_COUNT-1



    def available_cols(self):
        # Returns the full list of legal moves that for next player.
        available = []
        for i in range(COLUMN_COUNT):
            if( self.board[0][i] == 0 ):
                available.append(i)

        return available



    # Check if position is available (row not full)
    def try_move(self, col):
        return self.board[0][col] == 0
        


    # Check if the game has ended (no ore available columns to play in)
    def game_ended(self):
        if len(self.available_cols()) == 0:
            return True
        else:
            return False



    # Determines the next state by playing randomly
    def next_state(self, player):
        aux = copy.deepcopy(self)
        possible_moves = aux.available_cols()

        if len(possible_moves) > 0:
            col = np.random.choice(possible_moves)
            row = aux.get_next_open_row(col)
            aux.place_token(row, col, player)
            aux.last_move = [row, col]
        return aux



    # Find if most recent play was a winning move
    # There are two functions that try to achieve the same thing (determine if there is a winner)
    # However, is_winner looks at it irrelevant from who played last, and is more useful when exploring a state tree
    def winning_move(self, piece):
        # return False
        # Check horizontal locations for win
        for c in range(COLUMN_COUNT-3):
            for r in range(ROW_COUNT):
                if self.board[r][c] == piece and self.board[r][c+1] == piece and self.board[r][c+2] == piece and self.board[r][c+3] == piece:
                    return True
    
        # Check vertical locations for win
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT-3):
                if self.board[r][c] == piece and self.board[r+1][c] == piece and self.board[r+2][c] == piece and self.board[r+3][c] == piece:
                    return True
    
        # Check positively sloped diaganols
        for c in range(COLUMN_COUNT-3):
            for r in range(ROW_COUNT-3):
                if self.board[r][c] == piece and self.board[r+1][c+1] == piece and self.board[r+2][c+2] == piece and self.board[r+3][c+3] == piece:
                    return True
    
        # Check negatively sloped diaganols
        for c in range(COLUMN_COUNT-3):
            for r in range(3, ROW_COUNT):
                if self.board[r][c] == piece and self.board[r-1][c+1] == piece and self.board[r-2][c+2] == piece and self.board[r-3][c+3] == piece:
                    return True
                


    # Takes the board as input and determines if there is a winner.
    # If the game has a winner, it returns the player number (Player1 = 1, Player2 = -1).
    # If the game is still ongoing, it returns zero.  
    def is_winner(self):
        x = self.last_move[0]
        y = self.last_move[1]

        if x == None:
            return 0 

        for d in range(4):

            h_counter = 0
            c_counter = 0

            for k in range(-3,4):

                u = x + k * dx[d]
                v = y + k * dy[d]

                if u < 0 or u >= 6:
                    continue

                if v < 0 or v >= 7:
                    continue

                if self.board[u][v] == -1:
                    c_counter = 0
                    h_counter += 1
                elif self.board[u][v] == 1:
                    h_counter = 0
                    c_counter += 1
                else:
                    h_counter = 0
                    c_counter = 0

                if h_counter == 4:
                    return -1 

                if c_counter == 4:	
                    return 1

        return 0



    # Print the game board
    def print_board(self):
        # Print the game state in the console
        # board_copy = np.copy(self.board).astype(object)
        # for n in [-1, 0, 1]:
        #     board_copy[board_copy==n] = symbols[n]
        # print (board_copy)

        # Pygame GUI version
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
                pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
        
        # Draw the player tokens (RED or YELLOW)
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                if self.board[r][c] == 1:
                    pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int((ROW_COUNT-1-r)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
                elif self.board[r][c] == -1: 
                    pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int((ROW_COUNT-1-r)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
        pygame.display.update()



    # Reset game board
    def reset_board(self):
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                self.board[r][c] = 0



# NODE CLASS (build trees which algorithms will use)
class Node():
    # Data structure to keep track of algorithm searches
    # State represents boards at a given time
    def __init__(self, state, parent = None):
        self.visits = 1
        self.reward = 0.0
        self.state = state
        self.children = []
        self.children_move = []
        self.parent = parent



    # Nodes are chained together and hold references to their children nodes
    def add_child(self, child_state, move):
        child = Node(child_state, self)
        self.children.append(child)
        self.children_move.append(move)



    # Update the reward/weight for a node
    def update(self, reward):
        self.reward += reward
        self.visits += 1



    # Determines if there are still nodes to explore (TODO: I THINK?)
    def fully_explored(self):
        if len(self.children) == len(self.state.available_cols()):
            return True
        return False



# AI PLAYING TECHNIQUES -----------------
# 1. RANDOM
def play_random(player, game):
    # Choose a random available column
    if len(game.available_cols()) > 0:
        col = np.random.choice(game.available_cols())
        row = game.get_next_open_row(col)
        game.place_token(row, col, player)

        return True
    else:
        # No more columns available, game has ended (check if player won, else is draw)
        return False



# 2. MONTE CARLO TREE SEARCH
def MCTS(max_iter, root, factor, player):
    p = copy.deepcopy(player)
    for i in range(max_iter):
        front, p = tree_policy(root, player, factor)
        reward = default_policy(front.state, p)
        backpropagate(front, reward, p)

    ans = best_child(root, 0)
    print ((c.reward/c.visits) for c in ans.parent.children)
    return ans



# Determines next move by exploring the tree
def tree_policy(node, player, factor):
    while node.state.game_ended() == False and node.state.is_winner() == 0:
        if node.fully_explored() == False:
            return expand(node, player), -player
        else:
            node = best_child(node, factor)
            player *= -1
    return node, player
    


# Explores further nodes (moves) from a given fringe
def expand(node, player):
    tried_children_move = [m for m in node.children_move]
    possible_moves = node.state.available_cols()

    for col in possible_moves:
        if col not in tried_children_move:
            row = node.state.get_next_open_row(col)
            # Create a new node object that is an identical copy of the original
            new_state = copy.deepcopy(node.state)
            new_state.board[row][col] = player
            new_state.last_move = [row, col]
            break
    
    node.add_child(new_state, col)
    return node.children[-1]



# Calculates the UCB for all child nodes and returns a random child node from the best UCBs
def best_child(node, factor):
    best_score = -10000000.0
    best_children = []
    for c in node.children:
        # Calculate the UCB for each node
        node_value = c.reward / c.visits
        explore = math.sqrt(math.log(2.0 * node.visits) / float(c.visits))
        score = node_value + factor * explore
        if score == best_score:
            # Add to the list of best UCB child nodes
            best_children.append(c)
        if score > best_score:
            # Replace all previous child nodes with this one (best UCB)
            best_children = [c]
            best_score = score

    return np.random.choice(best_children)



# Determines the next state by playing randomly
def default_policy(state, player):
    while state.game_ended() == False and state.is_winner() == 0:
        state = state.next_state(player)
        player *= -1
    return state.is_winner()



# Update the current node sequence with the simulation result
def backpropagate(node, reward, player):
    while node != None:
        node.visits += 1
        node.reward -= player * reward
        node = node.parent
        player *= -1
    return



# 3. Minmax with alpha/beta pruning
# This algorithm works recursively
def minimax(state, depth, alpha, beta, maximisingPlayer, player):
    state_copy = copy.deepcopy(state)
    valid_locations = state_copy.available_cols()
    is_terminal = state_copy.game_ended() == False and len(valid_locations) == 0

    if depth == 0 or is_terminal:
        if is_terminal:
            # Weight the minmax player winning really high
            if state_copy.winning_move(player):
                return (None, 9999999)
            # Weight the other player winning really low
            elif state_copy.winning_move(-player):
                return (None, -9999999)
            else:  # No more valid moves
                return (None, 0)
        # Return the bot's score
        else:
            return (None, score_position(state_copy.board, player))

    if maximisingPlayer:
        value = -9999999
        # Randomise column to start
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = state_copy.get_next_open_row(col)

            # Drop a piece in the temporary board and record score
            state_copy.place_token(row, col, player)

            # Recursively calling itself (until depth is 0)
            new_score = minimax(state_copy, depth - 1, alpha, beta, False, -player)[1]

            if new_score > value:
                value = new_score
                # Make 'column' the best scoring column we can get
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimising player
        value = 9999999
        # Randomise column to start
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = state_copy.get_next_open_row(col)

            # Drop a piece in the temporary board and record score
            state_copy.place_token(row, col, -player)

            # Recursively calling itself (until depth is 0)
            new_score = minimax(state_copy, depth - 1, alpha, beta, True, -player)[1]
            if new_score < value:
                value = new_score
                # Make 'column' the best scoring column we can get
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

# TODO: UNDERSTAND THIS
def evaluate_window(window, player):
    score = 0
    # Switch scoring based on turn
    opp_player = -player

    # Prioritise a winning move
    # Minimax makes this less important
    if window.count(player) == 4:
        score += 100
    # Make connecting 3 second priority
    elif window.count(player) == 3 and window.count(0) == 1:
        score += 5
    # Make connecting 2 third priority
    elif window.count(player) == 2 and window.count(0) == 2:
        score += 2
    # Prioritise blocking an opponent's winning move (but not over bot winning)
    # Minimax makes this less important
    if window.count(opp_player) == 3 and window.count(0) == 1:
        score -= 4

    return score

# TODO: UNDERSTAND THIS
def score_position(board, player):
    score = 0

    # Score centre column
    centre_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    centre_count = centre_array.count(player)
    score += centre_count * 3

    # Score horizontal positions
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            # Create a horizontal window of 4
            window = row_array[c:c + 4]
            score += evaluate_window(window, player)

    # Score vertical positions
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            # Create a vertical window of 4
            window = col_array[r:r + 4]
            score += evaluate_window(window, player)

    # Score positive diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            # Create a positive diagonal window of 4
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, player)

    # Score negative diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            # Create a negative diagonal window of 4
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, player)

    return score



# PYGAME GUI AND INITIALIZATIONS ----------------------------------
# Initialize the board

# GAME VARIABLES
# Create a Connect4 object with a board and available columns tracker variables
game = C4()
# Determines the starting player (1 or -1)
player = 1
# Counts how many moves have been played in total
mvcntr = 1
# Track if the game is over or not (originally this is false)
game_over = False

# Initialize game
pygame.init()

# Define our screen size
SQUARESIZE = 100

# Define width and height of our board
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
game.print_board()
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)



## GAME LOOP --------------------------------------------------
while not game_over:

    # Let's have player 2 play using MCTS
    if player == -1:
        # play_random(player, game)

        # Get best move using MCTS
        o = Node(game)
        best_move = MCTS(MCTS_MAX_ITER, o, MCTS_FACTOR, player)
        game = copy.deepcopy(best_move.state)

        # Get best move using minmax
        # col, minimax_score = minimax(game, MINMAX_DEPTH, DEFAULT_ALPHA, DEFAULT_BETA, True, player)
        # if game.try_move(col):
        #     row = game.get_next_open_row(col)
        #     game.place_token(row, col, player)
        # else:
        #     print("nope!")



        if game.winning_move(player):
            label = myfont.render("Player 2 wins!!", 2, YELLOW)
            screen.blit(label, (40,10))
            game_over = True
        elif game.game_ended():
            label = myfont.render("Draw", 1, BLUE)
            screen.blit(label, (40,10))
            game_over = True

        # Mark the next player to play
        player *= -1

        # Increment move counter
        mvcntr += 1

        game.print_board()

        if game_over:
            pygame.time.wait(WAIT_TIME)
            game_over = False
            player = 1
            game.reset_board()
            game.print_board()

    # Player 1 is controlled by the player
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
    
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                posx = event.pos[0]
                if player == 1:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                else: 
                    pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()
    
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))

                # Ask for Player 1 Input
                if player == 1:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))
    
                    if game.try_move(col):
                        row = game.get_next_open_row(col)
                        game.place_token(row, col, player)
    
                        if game.winning_move(player):
                            label = myfont.render("Player 1 wins!!", 1, RED)
                            screen.blit(label, (40,10))
                            game_over = True
                        elif game.game_ended():
                            label = myfont.render("Draw", 1, BLUE)
                            screen.blit(label, (40,10))
                            game_over = True

                        # Mark the next player to play
                        player *= -1

                        # Increment move counter
                        mvcntr += 1
                
                game.print_board()

                if game_over:
                    pygame.time.wait(WAIT_TIME)
                    game_over = False
                    player = 1
                    game.reset_board()
                    game.print_board()