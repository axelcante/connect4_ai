import numpy as np
import random
import pygame
import sys
import math
import copy

# Followed the python tutorial by Siddhi Sawant - https://www.askpython.com/python/examples/connect-four-game
# Followed MCTS implementation by Alfredo de la Fuente - https://github.com/Alfo5123/Connect4/blob/master/README.md
# Followed Minmax with Alpha/Beta pruning implementation by Keith Galli - https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py

# BOARD CONFIG
ROW_COUNT = 6
COLUMN_COUNT = 7
# MCTS CONFIG
MCTS_MAX_ITER = 5000
MCTS_FACTOR = 2.0
# MINMAX CONFIG
MINMAX_DEPTH = 5
MINMAX_PLAYER = -1

# I cannot explain what this is for, only that Alfredo de la Fuente refers to it in their is_winner method
dx = [1, 1,  1,  0]
dy = [1, 0,  -1,  1]

# Pygame GUI RGB colors and time
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

# PYGAME DELAY BETWEEN GAMES AND TURNS
WAIT_TIME = 10000
TURN_DELAY = 2000

# Python dictionary to map integers (1, -1, 0) to characters ('x', 'o', ' ')
# Used only for console version
symbols = { 1:'x',
           -1:'o',
            0:' '}

# Determine which agent controls Player 1 or Player 2
# 4 choices: human, random selector, minmax algorithm or mcts
agents = { 0: 'player',
           1: 'rand',
           2: 'minmax',
           3: 'mcts' }



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
    def winning_move(self, player):
        # return False
        # Check horizontal locations for win
        for c in range(COLUMN_COUNT-3):
            for r in range(ROW_COUNT):
                if self.board[r][c] == player and self.board[r][c+1] == player and self.board[r][c+2] == player and self.board[r][c+3] == player:
                    return True
    
        # Check vertical locations for win
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT-3):
                if self.board[r][c] == player and self.board[r+1][c] == player and self.board[r+2][c] == player and self.board[r+3][c] == player:
                    return True
    
        # Check positively sloped diaganols
        for c in range(COLUMN_COUNT-3):
            for r in range(ROW_COUNT-3):
                if self.board[r][c] == player and self.board[r+1][c+1] == player and self.board[r+2][c+2] == player and self.board[r+3][c+3] == player:
                    return True
    
        # Check negatively sloped diaganols
        for c in range(COLUMN_COUNT-3):
            for r in range(3, ROW_COUNT):
                if self.board[r][c] == player and self.board[r-1][c+1] == player and self.board[r-2][c+2] == player and self.board[r-3][c+3] == player:
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



    # Determines if there are still nodes to explore
    def fully_explored(self):
        if len(self.children) == len(self.state.available_cols()):
            return True
        return False



# AI PLAYING TECHNIQUES -----------------
# 1. RANDOM
def play_random(game):
    # Choose a random available column
    if len(game.available_cols()) > 0:
        col = np.random.choice(game.available_cols())
        return col
    else:
        # No more columns available, game has ended (check if player won, else is draw)
        return -1



# 2. MONTE CARLO TREE SEARCH
def MCTS(max_iter, root, factor, player):
    p = copy.deepcopy(player)
    for i in range(max_iter):
        front, p = tree_policy(root, player, factor)
        reward = default_policy(front.state, p)
        backpropagate(front, reward, p)

    ans = best_child(root, 0)
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
    best_score = -math.inf
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
def minimax(state, depth, alpha, beta, maximizingPlayer):
    valid_locations = state.available_cols()
    is_terminal = is_terminal_node(state)

    if depth == 0 or is_terminal:
        if is_terminal:
            if state.winning_move(MINMAX_PLAYER):
                return (None, 100000000000000)
            elif state.winning_move(-MINMAX_PLAYER):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(state, MINMAX_PLAYER))
        
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = state.get_next_open_row(col)
            state_cp = copy.deepcopy(state)
            state_cp.place_token(row, col, MINMAX_PLAYER)
            new_score = minimax(state_cp, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        # print("MAX VALUE = ", value)
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = state.get_next_open_row(col)
            state_cp = copy.deepcopy(state)
            state_cp.place_token(row, col, -MINMAX_PLAYER)
            new_score = minimax(state_cp, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        # print("MIN VALUE = ", value)
        return column, value



# Determines if the game state is final (winner or draw)
def is_terminal_node(state):
    return state.winning_move(1) or state.winning_move(-1) or len(state.available_cols()) == 0



# This function is called in the below "score_position" method
# It simply applies a value to a given pattern (to avoid repeating it for all pattern cases)
def evaluate_window(window, player):
    score = 0
    # Switch scoring based on turn
    opp_player = -player

    # Prioritise a winning move
    # Minmax makes this less important
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



# Takes a given board state and applies a score to the relevant player
# This function counts desirable patterns (two in a row, three in a row, winner) which have a point weight 
# Minmax uses this to determine which moves are worth more (or less) when computing its optimal strategy
def score_position(state, player):
    score = 0

    # Score centre column
    centre_array = [int(i) for i in list(state.board[:, COLUMN_COUNT // 2])]
    centre_count = centre_array.count(player)
    score += centre_count * 3

    # Score horizontal positions
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(state.board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            # Create a horizontal window of 4
            window = row_array[c:c + 4]
            score += evaluate_window(window, player)

    # Score vertical positions
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(state.board[:, c])]
        for r in range(ROW_COUNT - 3):
            # Create a vertical window of 4
            window = col_array[r:r + 4]
            score += evaluate_window(window, player)

    # Score positive diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            # Create a positive diagonal window of 4
            window = [state.board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, player)

    # Score negative diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            # Create a negative diagonal window of 4
            window = [state.board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, player)

    return score



# PYGAME GUI AND INITIALIZATIONS ----------------------------------
# GAME VARIABLES
# Create a Connect4 object with a board and available columns tracker variables
game = C4()
# Determines the starting player (1 or -1)
player = 1
# Counts how many moves have been played in total
mvcntr = 1
# Track if the game is over or not (originally this is false)
game_over = False
# Track which players are currently playing against each other
# player_1_agent = agents[0] # 0 - HUMAN
# player_1_agent = agents[1] # 1 - RANDOM
# player_1_agent = agents[2] # 2 - MINMAX
player_1_agent = agents[3] # 3 - MCTS

# player_2_agent = agents[2] # 0 - HUMAN
# player_2_agent = agents[2] # 1 - RANDOM
player_2_agent = agents[2] # 2 - MINMAX
# player_2_agent = agents[2] # 3 - MCTS

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

    # Player 1 is controlled by the player or MCTS agent
    if player == 1:
        # Add a delay to avoid AI playing too fast
        pygame.time.wait(TURN_DELAY)

        # Player 1 can be human, MCTS or Minmax
        if player_1_agent == 'human':
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
        
                # Player 1 is controlled by the Player
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))

                    if player == 1:
                        posx = event.pos[0]
                        col = int(math.floor(posx/SQUARESIZE))

                        # Apply move to game state
                        if game.try_move(col):
                            row = game.get_next_open_row(col)
                            game.place_token(row, col, player)

        # Player 1 is controlled by MCTS agent
        elif player_1_agent == 'mcts':
            # Get best move using MCTS
            o = Node(game)
            best_move = MCTS(MCTS_MAX_ITER, o, MCTS_FACTOR, player)
            game = copy.deepcopy(best_move.state)

        # Player 1 is controlled by Minmax agent
        elif player_1_agent == 'minmax':
            col, minimax_score = minimax(game, MINMAX_DEPTH, -math.inf, math.inf, True)

            # Apply move to game state
            if game.try_move(col):
                row = game.get_next_open_row(col)
                game.place_token(row, col, player)
            
        # Detect if Player 1 has won
        if game.winning_move(player):
            label = myfont.render("Player 1 wins!!", 1, RED)
            screen.blit(label, (40,10))
            game_over = True
        # Detect if game has ended with no winner (DRAW)
        elif game.game_ended():
            label = myfont.render("Draw", 1, BLUE)
            screen.blit(label, (40,10))
            game_over = True

        # Mark the next player to play
        player *= -1

        # Increment move counter
        mvcntr += 1
        
        # Refresh game board
        game.print_board()

        # Reset game after delay when game has ended
        if game_over:
            pygame.time.wait(WAIT_TIME)
            game_over = False
            player = 1
            game.reset_board()
            game.print_board()
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
    
    # Let's have player 2 play using random or minmax agent or MCTS
    if player == -1:
        # Add a delay to avoid AI playing too fast
        pygame.time.wait(TURN_DELAY)

        # Player 1 is controlled by the player or MCTS agent
        if player_2_agent == 'human':
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
        
                # Player 1 is controlled by the Player
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))

                    if player == 1:
                        posx = event.pos[0]
                        col = int(math.floor(posx/SQUARESIZE))

                        # Apply move to game state
                        if game.try_move(col):
                            row = game.get_next_open_row(col)
                            game.place_token(row, col, player)

        # Player 1 is controlled by MCTS agent
        elif player_2_agent == 'mcts':
            # Get best move using MCTS
            o = Node(game)
            best_move = MCTS(MCTS_MAX_ITER, o, MCTS_FACTOR, player)
            game = copy.deepcopy(best_move.state)

        # Player 1 is controlled by Minmax agent
        elif player_2_agent == 'minmax':
            col, minimax_score = minimax(game, MINMAX_DEPTH, -math.inf, math.inf, True)

            # Apply move to game state
            if game.try_move(col):
                row = game.get_next_open_row(col)
                game.place_token(row, col, player)
            
        # Detect if Player 1 has won
        if game.winning_move(player):
            label = myfont.render("Player 1 wins!!", 1, RED)
            screen.blit(label, (40,10))
            game_over = True
        # Detect if game has ended with no winner (DRAW)
        elif game.game_ended():
            label = myfont.render("Draw", 1, BLUE)
            screen.blit(label, (40,10))
            game_over = True

        # Mark the next player to play
        player *= -1

        # Increment move counter
        mvcntr += 1
        
        # Refresh game board
        game.print_board()

        # Reset game after delay when game has ended
        if game_over:
            pygame.time.wait(WAIT_TIME)
            game_over = False
            player = 1
            game.reset_board()
            game.print_board()
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))