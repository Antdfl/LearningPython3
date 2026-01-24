from tkinter import *   # pyright:ignore
import pandas
import random

BACKGROUND_COLOR = "#B1DDC6"
FONT_TITLE = ("Arial", 40, "italic")
FONT_WORD = ("Arial", 60, "bold")
current_card = {}
data = None
#------------------------------ READING DATA ------------------------------------------#
try:
    data = pandas.read_csv('./flash-card-project/data/words_to_learn.csv')
except FileNotFoundError:
    data = pandas.read_csv("./flash-card-project/data/french_words.csv")
finally:
    to_learn_dict = data.to_dict(orient="records") # pyright:ignore

#-------------------------------- BUSINESS LOGIC --------------------------------------#
def next_card():
    global current_card, flip_timer
    window.after_cancel(flip_timer)
    canvas.itemconfig(canvas_background, image=card_front_img)
    current_card = random.choice(to_learn_dict)
    canvas.itemconfig(card_word, text=current_card["French"], fill="black")
    canvas.itemconfig(card_title, text="French", fill="black")
    flip_timer = window.after(3000, func=flip_card)

def flip_card():
    canvas.itemconfig(canvas_background, image=card_back_img)
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=current_card["English"], fill="white")

def is_known():
    global to_learn_dict, current_card
    to_learn_dict.remove(current_card)
    data_to_learn = pandas.DataFrame(to_learn_dict)
    data_to_learn.to_csv('./flash-card-project/data/words_to_learn.csv', index=False)
    next_card()

#------------------------------- UI SETUP ---------------------------------------------#

window = Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)
flip_timer = window.after(3000, func=flip_card)

canvas = Canvas(window, width=800, height=526 ,highlightthickness=0, bg=BACKGROUND_COLOR)
card_front_img = PhotoImage(file="./flash-card-project/images/card_front.png")
card_back_img = PhotoImage(file="./flash-card-project/images/card_back.png")
canvas_background = canvas.create_image(400, 263, image=card_front_img)
canvas.grid(row=0, column=0, columnspan=2)

card_title = canvas.create_text(400, 150, font=FONT_TITLE, text="Title")
card_word = canvas.create_text(400, 263, font=FONT_WORD, text="Word")

img_unknown = PhotoImage(file="./flash-card-project/images/wrong.png")
btn_unknown = Button(image=img_unknown, highlightthickness=0, command=next_card)
btn_unknown.grid(row=1, column=0)

img_known = PhotoImage(file="./flash-card-project/images/right.png")
btn_known = Button(image=img_known, highlightthickness=0, command=is_known)
btn_known.grid(row=1, column=1)

next_card()

# window.after_cancel(timer)

window.mainloop()
