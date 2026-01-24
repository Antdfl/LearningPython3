from art import logo
print(logo)
# TODO-1: Ask the user for input
def find_highest_bidder(bidding_dictionary):
     winner =""
     highest_bid = 0
     for bidder in participant_dict:
         bid_amount = bidding_dictionary[bidder]
         if bid_amount > highest_bid:
            winner = bidder
            highest_bid = bid_amount
     print(f"The winner is {winner} with a bid of ${highest_bid}")


should_continue = True
participant_dict = {}
print("Welcome to the secret auction program.")
while should_continue:
    name = input("What is your name? ")
    bid = float(input("What's your bid?: $"))
    participant_dict[name] = bid
    other_bidders = input("Are there other bidders? Type 'yes' or 'no'\n")
    if other_bidders == "yes":
        should_continue = True
        print("\n" * 20)
    else:
        should_continue = False
        find_highest_bidder(participant_dict)


