from turtle import Turtle
MOVE_DISTANCE = 20
UP = 90
DOWN = 270
# coord init is a tuple that contains (x,y) coordinates of the initial paddle's visualization
class Paddle(Turtle):
    def __init__(self, coord_init):
        super().__init__()
        self.shape("square")
        self.color("white")
        self.shapesize(stretch_wid=5, stretch_len=1)
        self.penup()
        self.goto(coord_init)

    def go_up(self):
        new_y = self.ycor() + MOVE_DISTANCE
        print(new_y)
        if new_y > 250 or new_y < -250:
            return
        self.goto(self.xcor(), new_y)

    def go_down(self):
        new_y = self.ycor() - MOVE_DISTANCE
        print(new_y)
        if new_y > 250 or new_y < -250:
            return
        self.goto(self.xcor(), new_y)

