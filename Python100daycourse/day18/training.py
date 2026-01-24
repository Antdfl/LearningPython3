import random
import turtle as t
from zipfile import sizeEndCentDir

tim = t.Turtle()
# colours = ["dark gray","cornflower blue","deep sky blue",
#           "green yellow","gold","sienna","orange red","pink",
#           "magenta","indigo","bisque","dark green","khaki"]
t.colormode(255)
direction =[0, 90, 180, 270]

def random_color():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    colour = (r,g,b)
    return colour

# Draw a spirograph
tim.pensize(1)
radius = 100
tim.speed("fastest")

def draw_spirograph(size_of_gap):
    for _ in range(int(360 / size_of_gap)):
        tim.pencolor(random_color())
        tim.circle(radius)
        tim.setheading(tim.heading() + size_of_gap)
    tim.hideturtle()

draw_spirograph(5)
screen = t.Screen()
screen.exitonclick()
# import heroes
# print(heroes.gen())

# Draw polygon from a triangle to a decagon choosing each time a different colour
# for i in range(3,11):
#     angle = 360/(i+1)
#     color = choice(colours)
#     tim.color(color)
#     for j in range(i):
#         tim.forward(100)
#         tim.right(angle)

# Draw a dashed line with
# for i in range(10):
#      tim.pendown()
#      tim.forward(10)
#      tim.penup()
#      tim.forward(10)

# # draw a random walk
# tim.pensize(1)
# line_length = 30
# tim.speed("fastest")
# for _ in range(200):
#     tim.forward(line_length)
#     tim.color(random_color())
#     tim.setheading(random.choice(direction))

