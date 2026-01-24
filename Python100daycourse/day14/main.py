from game_data import data
from art import logo,vs
import random
# You need data. Ok, you got it
print(logo)
score = 0

def format_data(data_list, index):
    return (f"{data[index]["name"]}, a {data[index]["description"]}, "
            f"from {data[index]["country"]}")

item_B_index = random.randint(0,50)
game_over = False
while not game_over:
    # compare the two values of the one you chose with the other's value
    item_A_index = item_B_index
    item_B_index = random.randint(0, 50)

    if item_B_index == item_A_index:
        item_B_index = random.randint(0, 50)
    print(f"Compare A: {format_data(data, item_A_index)}")
    print(vs)
    print(f"Against B: {format_data(data, item_B_index)}")
    # Give user choice
    user_choice = input("Who has more followers? Type 'A' or 'B': ").upper()
    print("\n" * 30)
    print(logo)
    # Extract data from both
    A_num_of_followers = data[item_A_index]["follower_count"]
    B_num_of_followers = data[item_B_index]["follower_count"]
    # Associate the A and B data to user_followers_associated
    # while the other value will be associated to other_followers_associate variable
    if user_choice == "A":
        user_followers_associated = A_num_of_followers
        other_followers_associated = B_num_of_followers
    else:
        user_followers_associated = B_num_of_followers
        other_followers_associated = A_num_of_followers
    # print(f"user_followers_associated {user_followers_associated} "
    #       f"vs other_followers_associated {other_followers_associated}")
    if user_followers_associated > other_followers_associated:
        # In case you won, add 1 point to the counter
        score +=1
        print(f"You're right! Current user score {score}.")
    else:
        # If you lose. Game Over.
        print(f"Sorry, that's wrong. Final user score {score}")
        game_over = True