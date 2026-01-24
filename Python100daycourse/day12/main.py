import random
from art import logo
print(logo)
# Manage the initialization of variables
EASY_LEVEL_TURNS = 10
HARD_LEVEL_TURNS = 5
print("Welcome to the number Guessing Game!")
# Generating a random number
chosen_number = random.randint(1,100)
#print(chosen_number)
print("I'm thinking a number between 1 and 100.")

# Choose number_of_attempts based on the difficulty level
def set_diff_lvl():
    choose_a_diff_lvl = True
    num_of_attempts = 0
    while choose_a_diff_lvl:
        difficulty_level = input("Choose a difficulty. Type 'easy or 'hard': ")
        if difficulty_level == "easy":
            num_of_attempts = EASY_LEVEL_TURNS
            choose_a_diff_lvl = False
        elif difficulty_level == "hard":
            num_of_attempts = HARD_LEVEL_TURNS
            choose_a_diff_lvl = False
        else:
            print(f"The allowed two levels are 'easy' or 'hard'. You typed {difficulty_level}")
    return num_of_attempts
# Core function: based on the difficulty level loop until
# you guess the number or run out of attempts
# This function returns True only for the correct answer
def check_answer(guess_num, actual_number):
    if guess_num > chosen_number:
        print("Too High.")
        return False
    elif guess_num < actual_number:
        print("Too Low.")
        return False
    else:
        print(f"You got it! The right answer was {actual_number}")
        return True

def game(num_attempts):
    for i in range(num_attempts):
        guess = int(input("Make a guess: "))
        correct_answer = check_answer(guess, chosen_number)
        if not correct_answer:
            num_attempts -= 1
            if num_attempts == 0:
                print(f"You run out of attempts. You lose. The actual number was {chosen_number}")
            else:
               print("Guess again")
               print(f"You have {num_attempts} left to guess the number")
        else:
            break

number_of_attempts = set_diff_lvl()
print(f"You have {number_of_attempts} left to guess the number")
game(number_of_attempts)


