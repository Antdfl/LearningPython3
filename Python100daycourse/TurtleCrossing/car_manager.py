import random
from turtle import Screen,Turtle
COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
STARTING_MOVE_DISTANCE = 5
MOVE_INCREMENT = 10


class CarManager(Turtle):
    def __init__(self):
        super().__init__()
        self.all_cars = []
        self.hideturtle()
        self.car_speed = STARTING_MOVE_DISTANCE

    def create_car(self):
        random_chance = random.randint(1,6)
        if random_chance == 1:
            new_car = Turtle()
            new_car.shape("square")
            new_car.shapesize(stretch_wid=1, stretch_len=2)
            new_car.penup()
            new_car.setheading(180)
            new_car.color(random.choice(COLORS))
            new_car.x_position = 300
            new_car.y_position = random.randint(-250, 250)
            new_car.goto(new_car.x_position, new_car.y_position)
            self.all_cars.append(new_car)

    def move_cars(self):
        for car in self.all_cars:
            car.x_position -= self.car_speed
            car.goto(car.x_position,car.y_position)

    def level_up(self):
        self.car_speed += MOVE_INCREMENT

