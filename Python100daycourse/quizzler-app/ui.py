import tkinter as tk
import quiz_brain
from quiz_brain import QuizBrain
import os
from pathlib import Path

CURRENT_WORKING_DIR = os.getcwd()
SCRIPT_DIR = Path(__file__).parent.resolve()
IMAGE_DIR = SCRIPT_DIR / "images"
# print(f"Current working dir: {CURRENT_WORKING_DIR}")
# print(f"Script dir: {SCRIPT_DIR}")
# print(f"Image dir: {IMAGE_DIR}")

THEME_COLOR = "#375362"
FONT_SCORE = ("Arial",12,"normal")
FONT_QUESTION = ("Arial",18, "italic")

class QuizInterface:
    def __init__(self, quiz_brain):
        self.quiz = quiz_brain
        self.window = tk.Tk()
        self.window.title("Quizzler")
        #self.window.geometry("400x400")
        self.window.config(padx=20, pady=20, background=THEME_COLOR)
        #self.window.resizable(width=False, height=False)

        self.lbl_score = tk.Label(text="Score: 0", font=FONT_SCORE, bg=THEME_COLOR, fg="white")
        self.lbl_score.grid(row=0, column=1)

        self.canvas = tk.Canvas(self.window, width=300, height=250, highlightthickness=0, bg="white")
        self.question_text = self.canvas.create_text(150, 125, width=270, font=FONT_QUESTION,
                                                     text="Some Questions (True/False)",
                                                     fill="black")
        self.canvas.grid(row=1, column=0, columnspan=2, pady=50)


        self.img_true = tk.PhotoImage(file=f"{IMAGE_DIR}/true.png")
        self.btn_true = tk.Button(image=self.img_true, highlightthickness=0, command=self.true_pressed)
        self.btn_true.grid(row=2, column=0)

        self.img_false = tk.PhotoImage(file=f"{IMAGE_DIR}/false.png")
        self.btn_false = tk.Button(image=self.img_false, highlightthickness=0, command=self.false_pressed)
        self.btn_false.grid(row=2, column=1)

        self.next_question()

        self.window.mainloop()

    def next_question(self):
        self.canvas.config(bg="white")
        self.lbl_score.config(text=f"Score: {self.quiz.score}")
        if self.quiz.still_has_questions():
            q_text = self.quiz.next_question()
            self.canvas.itemconfig(self.question_text, text=q_text)
        else:
            q_text = f"You've completed the quiz!\nYour final score was: {self.quiz.score}/{self.quiz.question_number}"
            self.canvas.itemconfig(self.question_text, text=q_text)
            self.btn_true.config(state="disabled")
            self.btn_false.config(state="disabled")

    def true_pressed(self):
        self.give_feedback(self.quiz.check_answer("True"))

    def false_pressed(self):
        self.give_feedback(self.quiz.check_answer("False"))

    def give_feedback(self, is_right :bool):
       if is_right:
           self.canvas.config(bg="green")
       else:
           self.canvas.config(bg="red")
       self.window.after(1000, self.next_question)