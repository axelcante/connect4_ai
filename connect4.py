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

# This array keeps tracks of which columns are still available to play in (0 if play available, 1 if full)
cols_tracker = np.zeros(COLUMN_COUNT)

# Python dictionary to map integers (1, -1, 0) to characters ('x', 'o', ' ')
# Used only for console version
symbols = { 1:'x',
           -1:'o',
            0:' '}



# Create an empty 6x7 array serving as the game board
def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board



# Select a random column to play (if possible)
def play_random(player, board):
    # Choose a random available column 
    available_cols = np.where(cols_tracker == 0)[0]

    if available_cols.size > 0:
        col = np.random.choice(available_cols)
        row = get_next_open_row(board, col)
        place_token(board, row, col, player)

        return True
    else:
        # No more columns available, game has ended (check if player won, else is draw)
        return False



# Drop a token in a select column
def place_token(board, row, col, player):
    board[row][col] = player
    # If token is placed in last possible row, mark that column as filled
    if row == ROW_COUNT - 1:
        cols_tracker[col] = 1



# Find the first available row (starting from the bottom)
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col]==0:
            return r



# Check if position is available (row not full)
# Not needed when playing randomly, used when playing manually
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0



# Find if most recent play was a winning move
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
 
    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
 
    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
 
    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True



# Print the game board in the console (for now)
def print_board(board):
    # Pygame GUI version
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
     
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):      
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == -1: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

    # Old console version
    board_copy = np.copy(np.flip(board)).astype(object)
    for n in [-1, 0, 1]:
        board_copy[board_copy==n] = symbols[n]
    print (board_copy)



# PYGAME GUI AND INITIALIZATIONS ----------------------------------
# Initialize the board
board = create_board()

# Game variables
player = 1
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
print_board(board)
pygame.display.update()


myfont = pygame.font.SysFont("monospace", 75)


## GAME LOOP --------------------------------------------------
while not game_over:

    # Let's have player 2 play automatically (randomly)
    if player == -1:
        play_random(player, board)

        if winning_move(board, player):
            label = myfont.render("Player 2 wins!!", 2, YELLOW)
            screen.blit(label, (40,10))
            game_over = True

        # Mark the next player to play
        player *= -1

        # Increment move counter
        mvcntr += 1

        print_board(board)

        if game_over:
            pygame.time.wait(3000)

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
    
                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        place_token(board, row, col, player)
    
                        if winning_move(board, player):
                            label = myfont.render("Player 1 wins!!", 1, RED)
                            screen.blit(label, (40,10))
                            game_over = True

                        # Mark the next player to play
                        player *= -1

                        # Increment move counter
                        mvcntr += 1
                
                print_board(board)

                if game_over:
                    pygame.time.wait(3000)
    
                # # # Ask for Player 2 Input
                # else:
                #     posx = event.pos[0]
                #     col = int(math.floor(posx/SQUARESIZE))
    
                #     if is_valid_location(board, col):
                #         row = get_next_open_row(board, col)
                #         place_token(board, row, col, player)
    
                #         if winning_move(board, 2):
                #             label = myfont.render("Player 2 wins!!", 1, YELLOW)
                #             screen.blit(label, (40,10))
                #             game_over = True

                #         # Mark the next player to play
                #         player *= -1

                #         # Increment move counter
                #         mvcntr += 1