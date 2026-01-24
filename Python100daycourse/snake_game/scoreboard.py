from turtle import Turtle
ALIGNMENT = "center"
FONT = ("Arial", 15, "normal")
from pathlib import Path

script_dir = Path(__file__).parent
file_path = script_dir / "data.txt"

class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        with open(file_path, "r") as file:
            high_score_str = file.read()
            print(high_score_str)
            if high_score_str.isdigit():
                self.high_score = int(high_score_str)
            else:
                self.high_score = 0
        #
        self.color("white")
        self.hideturtle()
        self.penup()
        self.goto(0, 270)
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        self.write(f"Score: {self.score} High Score: {self.high_score}", align=ALIGNMENT, font=FONT)

    def increase_score(self):
        self.score += 1
        self.update_scoreboard()

    def reset(self) -> None:
        if self.score > self.high_score:
            self.high_score = self.score 
            with open(file_path, "w") as file:
                file.write(f"{self.high_score}")
        self.score = 0
        self.update_scoreboard()

    # def game_over(self):
    #     self.goto(0, 0)
    #     self.write("GAME OVER", align=ALIGNMENT, font=FONT)