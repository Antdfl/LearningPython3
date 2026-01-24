import random

def display_board(board):
    # The function accepts one parameter containing the board's current status
    # and prints it out to the console.
    print("+","-" * 9,"+")
    for row in board:
        print("|"," | ".join(row),"|")
        print("+","-" * 9,"+")

def enter_move(board):
    # The function accepts the board's current status, asks the user about their move, 
    # checks the input, and updates the board according to the user's decision.
    while True:
        try:
            row = int(input("Enter the row (0-2): "))
            col = int(input("Enter the column (0-2): "))
            if (row, col) in make_list_of_free_fields(board):
                board[row][col] = "O"
                break
            else:
                print("Invalid move. Try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter numbers between 0 and 2.")

def make_list_of_free_fields(board):
    # The function browses the board and builds a list of all the free squares; 
    # the list consists of tuples, while each tuple is a pair of row and column numbers.
    free_fields = []
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == " ":
                free_fields.append((i, j))
    return free_fields


def victory_for(board, sign):    
    # The function analyzes the board's status in order to check if 
    # the player using 'O's or 'X's has won the game
    # Check rows and columns
    for i in range(3):
        # Check row
        if all(board[i][j] == sign for j in range(3)):
            return True
        # Check column
        if all(board[j][i] == sign for j in range(3)):
            return True
    # Check diagonals
    if all(board[i][i] == sign for i in range(3)):
        return True
    if all(board[i][2 - i] == sign for i in range(3)):
        return True
    return False

def draw_move(board):
    # The function draws the computer's move and updates the board.
    free_fields = make_list_of_free_fields(board)
    if free_fields:
        row, col = random.choice(free_fields)
        board[row][col] = "X"

# create an empty board
board = [[" " for _ in range(3)] for _ in range(3)]
draw_move(board)
while True:
    display_board(board)
    enter_move(board)
    if victory_for(board, "O"):
        print("Congratulations! You have won!")
        break
    elif not make_list_of_free_fields(board):
        print("It's a draw!")
        break
    draw_move(board)
    display_board(board)
    if victory_for(board, "X"):
        print("Computer has won!")
        break
    elif not make_list_of_free_fields(board):
        print("It's a draw!")
        break
