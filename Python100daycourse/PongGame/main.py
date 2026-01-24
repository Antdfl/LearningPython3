from turtle import Screen, Turtle
from paddle import Paddle
from ball import Ball
from scoreboard import Scoreboard
import time

screen = Screen()
screen.setup(width=800, height=600)
screen.bgcolor("black")
screen.title("Pong Game")
screen.tracer(0)

r_paddle = Paddle((350,0))
l_paddle= Paddle((-350,0))
ball = Ball()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(r_paddle.go_up, "Up")
screen.onkey(r_paddle.go_down,"Down")
screen.onkey(l_paddle.go_up, "w")
screen.onkey(l_paddle.go_down,"s")

game_on = True
while game_on:
    #print(f"ball.move_speed= {ball.move_speed}")
    ball.move()
    time.sleep(ball.move_speed)
    screen.update()
    if ball.ycor() > 280 or ball.ycor() < -280:
        ball.bounce_y()

    # Collision with paddles
    #print(f"ball distance r / l paddle: {ball.distance(r_paddle)}, {ball.distance(l_paddle)}")
    if ((ball.distance(r_paddle) < 50 and ball.xcor()> 320) or
            (ball.distance(l_paddle) < 40 and ball.xcor()< -320)):
        ball.bounce_x()
        scoreboard.update_scoreboard()

   # Detect right paddle miss
    if ball.xcor() > 380:
        ball.reset_position()
        scoreboard.l_point()
        scoreboard.update_scoreboard()

    # Detect left paddle miss
    if ball.xcor() < -380:
        ball.reset_position()
        scoreboard.r_point()
        scoreboard.update_scoreboard()

screen.exitonclick()