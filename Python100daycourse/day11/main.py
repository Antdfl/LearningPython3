import random
from art import logo

def deal_card():
    cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    card = random.choice(cards)
    return card

def sum_cards(scards):
    res: int = 0
    for num in scards:
        if res > 10 and num == 11:
             res +=1
        else:
            res += num
    return res

def compare(u_score, c_score):
    if  c_score == u_score:
        return "Draw"
    elif c_score > 21:
        return "Opponent went over. You win!"
    elif u_score > 21:
        return "You wen over. You lose."
    elif c_score == 21:
      return "Computer won with a BlackJack!"
      return
    elif c_score > u_score:
       return "You lose"
    else:
       return "You win!"

game_choice = True
def play_game():
    your_cards = []
    computer_cards =[]
    is_game_over = False
    computer_score = 0
    user_score = 0
    #
    print(logo)
    for i in range(2):
        your_cards.append(deal_card())
        computer_cards.append(deal_card())
    user_score = sum_cards(your_cards)
    computer_score = sum_cards(computer_cards)
    # Check for Blackjack for both players
    if user_score == 21 and computer_score < 21:
        print("You have a blackjack: You won!")
        is_game_over = True
    elif user_score < 21 and computer_score == 21:
        print("Computer has a blackjack: Computer won.")
        is_game_over = True

    # Nobody has a Blackjack: normal situation
    print(f"Your cards: {your_cards}, current score: {user_score}")
    print(f"Computer's first card {computer_cards[0]}")
    # Managing dealing card to the user
    another_card = True
    while another_card and not is_game_over:
        user_choice = input("Type 'y' to get another card, type 'n' to pass: ")
        if user_choice == "n":
            another_card = False
        else:
            your_cards.append(deal_card())
            user_score = sum_cards(your_cards)
            print(f"Your cards: {your_cards}, current score: {user_score}")
    # Let the computer play
    while computer_score <= 21 and computer_score < 17 and not is_game_over:
         computer_cards.append(deal_card())
         computer_score = sum_cards(computer_cards)
    print(f"Computer's final score {computer_score}")
    print(compare(user_score, computer_score))

while input("Do you want to play a game of Blackjack? Type 'y' or 'n': ") == 'y':
    print("\n" * 20)
    play_game()