# from turtle import Turtle, Screen
# import another_module
# print(another_module.another_variable)

# timmy = Turtle()
# print(timmy)
# timmy.shape("turtle")
# timmy.color("DarkGoldenrod1")
# my_screen = Screen()
# print(my_screen.canvheight)
# timmy.forward(100)
# timmy.left(120)
# timmy.forward(100)
# timmy.left(120)
# timmy.forward(100)
# my_screen.exitonclick()

from prettytable import PrettyTable

table = PrettyTable()
table.add_column("Pokemon name",["Pikachu","Squirtle","Charmander"])
table.add_column("Type",["Electric","Water","Faire"])
table.align = "r"
print(table)
