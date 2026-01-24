import time
from random import randint
from turtle import Screen
from player import Player
from car_manager import CarManager
from scoreboard import Scoreboard

screen = Screen()
screen.setup(width=600, height=600)
screen.tracer(0)

player = Player()
car_manager = CarManager()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(player.go_up, "Up")

game_is_on = True
while game_is_on:
    car_manager.move_cars()
    car_manager.create_car()
    for car in car_manager.all_cars:
        if car.distance(player) < 20:
            scoreboard.game_over()
            game_is_on = False
    if player.is_at_the_finish_line():
        car_manager.level_up()
        scoreboard.increase_level()
        player.go_to_start()
    time.sleep(0.1)
    screen.update()

screen.exitonclick()