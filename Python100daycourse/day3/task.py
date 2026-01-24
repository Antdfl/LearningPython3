from selectors import SelectSelector

print(r'''
*******************************************************************************
          |                   |                  |                     |
 _________|________________.=""_;=.______________|_____________________|_______
|                   |  ,-"_,=""     `"=.|                  |
|___________________|__"=._o`"-._        `"=.______________|___________________
          |                `"=._o`"=._      _`"=._                     |
 _________|_____________________:=._o "=._."_.-="'"=.__________________|_______
|                   |    __.--" , ; `"=._o." ,-"""-._ ".   |
|___________________|_._"  ,. .` ` `` ,  `"-._"-._   ". '__|___________________
          |           |o`"=._` , "` `; .". ,  "-._"-._; ;              |
 _________|___________| ;`-.o`"=._; ." ` '`."\ ` . "-._ /_______________|_______
|                   i| |o ;    `"-.o`"=._``  '` " ,__.--o;   |
|___________________|_| ;     (#) `-.o `"=.`_.--"_o.-; ;___|___________________
____/______/______/___|o;._    "      `".o|o_.--"    ;o;____/______/______/____
/______/______/______/_"=._o--._        ; | ;        ; ;/______/______/______/_
____/______/______/______/__"=._o--._   ;o|o;     _._;o;____/______/______/____
/______/______/______/______/____"=._o._; | ;_.--"o.--"_/______/______/______/_
____/______/______/______/______/_____"=.o|o_.--""___/______/______/______/____
/______/______/______/______/______/______/______/______/______/______/_____ /
*******************************************************************************
''')
print("Welcome to Treasure Island.")
print("Your mission is to find the treasure.")
direction = input("Where do you wanna go? left or right? ").lower()
if direction == "right":
    print("You fell into a hole. Game over")
elif direction == "left":
  action = input("Do you want to swim or wait? ").lower()
  if action == "swim":
      print("You drown sucked by the tides. Game Over")
  elif action == "wait":
      colour = input("You have in front three doors of different colour"
                     "(blue, red or yellow). Which colour do you choose?").lower()
      if colour == "blue":
          print("You ended up in landfill. Game over")
      elif colour == "red":
          print("You ended in a fire. Game over")
      elif colour == "yellow":
          print("You won!!!!!")
      else:
          print("Wrong choice of colour")
  else:
      print("wrong choice of action. Game Over.")
else:
    print("wrong choice of direction. Game Over.")