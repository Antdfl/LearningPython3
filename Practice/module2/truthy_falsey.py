import os
os.system('cls' if os.name == 'nt' else 'clear')

name=''
while not name:
    name = input("Enter your name: ")
    print("Hi " + name + ", How many guests will be attending?")
    try:
        numOfGuests = int(input())
    except ValueError:
        numOfGuests = 0
        print("Invalid input. Number of guests set to 0.")
    if numOfGuests:
        print("Be sure you have enough room for everyone!")
    print("Done")
