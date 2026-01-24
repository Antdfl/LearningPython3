import random
rock = '''
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
'''

paper = '''
    _______
---'   ____)____
          ______)
          _______)
         _______)
---.__________)
'''

scissors = '''
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
'''
games_images = [rock, paper, scissors]
user_choice = int(input("What do you choose? 0 for Rock, 1 for Paper, 2 for Scissors"))
user_choice_str = str(user_choice)
comp_choice_num = random.randint(0,2)
computer_choice = str(comp_choice_num)
# Rock beats Scissors.
# Scissors beat Paper.
# Paper beats Rock.
you_win = ["02", "10","21"]
draw = ["00","11","22"]
if user_choice_str != "0" and user_choice_str != "1" and user_choice_str !="2":
    print("You typed an invalid number. You lose!")
else:
    print(games_images[user_choice])
    print("Computer chose:")
    print(games_images[comp_choice_num])
    # Comparison
    comp_string = user_choice_str + computer_choice
    #print(comp_string)
    if comp_string in you_win:
        print("You win!")
    elif comp_string in draw:
        print("It's a Draw")
    else:
        print("You lose")