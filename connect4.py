import numpy as np
import pygame
import sys
import math

# Followed the python tutorial https://www.askpython.com/python/examples/connect-four-game

ROW_COUNT = 6
COLUMN_COUNT = 7

# Pygame GUI RGB colors
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

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
        # A 1D array tracking which columns are full (-1 if they are)
        self.cols_tracker = np.arange(COLUMN_COUNT)
        # TODO: NO IDEA WHAT THIS IS FOR
        self.last_move = [None, None]



    # Drop a token in a select column
    def place_token(self, row, col, player):
        self.board[row][col] = player
        # If token is placed in last possible row, mark that column as filled
        if row == ROW_COUNT - 1:
            self.cols_tracker[col] = -1



    # Find the first available row (starting from the bottom)
    def get_next_open_row(self, col):
        for r in range(ROW_COUNT):
            if self.board[r][col]==0:
                return r




    def available_cols(self):
        return np.where(self.cols_tracker != -1)[0]


    # Check if position is available (row not full)
    def try_move(self, col):
        return self.board[ROW_COUNT-1][col] == 0
        


    # Check if the game has ended (no ore available columns to play in)
    def game_ended(self):
        if len(self.available_cols()) == 0:
            return True
        else:
            return False




    # Determines the next state
    # TODO: NOT SURE WHAT THIS DOES
    def next_state(self, player):
        board_copy = np.copy(self.board)

        if len(self.available_cols) > 0:
            col = np.random.choice(self.available_cols())
            row = self.get_next_open_row(col)
            self.place_token(row, col, player)
            self.last_move = [row, col]
        return board_copy



    # Find if most recent play was a winning move
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



    # Print the game board
    def print_board(self):
        # Pygame GUI version
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
                pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
        
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):      
                if self.board[r][c] == 1:
                    pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
                elif self.board[r][c] == -1: 
                    pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
        pygame.display.update()

        # Old console version
        board_copy = np.copy(np.flip(self.board)).astype(object)
        for n in [-1, 0, 1]:
            board_copy[board_copy==n] = symbols[n]
        print (board_copy)



# NODE CLASS (build trees which algorithms will use)
class Node():
    # Data structure to keep track of algorithm searches
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
    # TODO: .size VS len()?
    if game.available_cols().size > 0:
        col = np.random.choice(game.available_cols())
        row = game.get_next_open_row(col)
        game.place_token(row, col, player)

        return True
    else:
        # No more columns available, game has ended (check if player won, else is draw)
        return False

# 2. MONTE CARLO TREE SEARCH




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

    # Let's have player 2 play automatically (randomly)
    if player == -1:
        play_random(player, game)

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
            pygame.time.wait(3000)

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
                #print(event.pos)

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
                    pygame.time.wait(3000)