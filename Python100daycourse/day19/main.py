import turtle
from turtle import Turtle, Screen
import random
screen = Screen()
screen.setup(width=800, height=600)
is_race_on=False

user_bet = screen.textinput("Make your choice?", "Which turtle will win the race?")
print(user_bet)

colors = ["red", "orange", "yellow", "green", "blue", "purple"]
y_positions = [150, 110, 70, 30, -10, -50]
ini_turtle_name = "turtle"
all_turtle = []
for turtle_index in range(len(colors)):
    new_turtle = Turtle(shape="turtle")
    new_turtle.speed("fastest")
    new_turtle.color(colors[turtle_index])
    new_turtle.penup()
    new_turtle.goto(x=-380, y=y_positions[turtle_index])
    all_turtle.append(new_turtle)

if user_bet:
    is_race_on = True

while is_race_on:
    for turtle in all_turtle:
        if turtle.xcor() > 380:
            if user_bet == turtle.pencolor():
                print("You won")
            else:
                print(f"You lost. The {turtle.pencolor()} was the winner.")
            is_race_on = False
        rand_distance = random.randint(0,20)
        turtle.forward(rand_distance)

screen.exitonclick()
















# def move_forwards():
#     tim.forward(10)
#
# def move_backwards():
#     tim.backward(10)
#
# def move_clockwise():
#     tim.right(10)
#
# def move_counterclockwise():
#     tim.left(10)
#
# def clear_screen():
#     tim.clear()
#     tim.penup()
#     tim.home()
#     tim.pendown()
#
# screen.listen()
# screen.onkey(key="w", fun=move_forwards)
# screen.onkey(key="s", fun=move_backwards)
# screen.onkey(key="a", fun=move_clockwise)
# screen.onkey(key="d", fun=move_counterclockwise)
# screen.onkey(key="c", fun=clear_screen)
# screen.exitonclick()