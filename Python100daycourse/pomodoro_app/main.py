import tkinter as tk
import math
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS # pyright:ignore
    except Exception:
        # When not bundled by PyInstaller, use the directory of this file
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)
# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
reps = 0
#timer = None

# ---------------------------- TIMER RESET ------------------------------- # 
def reset_timer():
    global reps, timer
    window.after_cancel(timer) # pyright: ignore[reportOptionalMemberAccess]
    reps = 0
    lbl_title.config(text="Timer", fg=GREEN)
    canvas.itemconfig(timer_text, text="00:00")
    lbl_checkmark.config(text="")

# ---------------------------- TIMER MECHANISM ------------------------------- # 
def start_timer():
    global reps
    reps += 1

    work_secs = int(WORK_MIN * 60)
    short_break_secs = int(SHORT_BREAK_MIN * 60)
    long_break_secs = int(LONG_BREAK_MIN * 60)
    #print(f"reps before {reps}")
    if reps % 8 == 0:
        lbl_title.config(text="Break", fg=RED)
        count_down(long_break_secs)
    elif reps % 2 == 0:
        lbl_title.config(text="Break", fg=PINK)
        count_down(short_break_secs)
    elif reps % 2 != 0:
        lbl_title.config(text="Work", fg=GREEN)
        count_down(work_secs)

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #

def count_down(count):
    global reps, timer
    count_min = int(math.floor(count / 60))
    count_sec = int(count % 60)
    if count_sec < 10:
        count_sec = f"0{count_sec}"
    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if count > 0:
        timer = window.after(1000, count_down, count-1)
    else:
        start_timer()
        #print(f"reps count down{reps}")
        marks = ""
        work_sessions = math.floor(reps/2)
        for _ in range(work_sessions):
            marks += "✔"
        lbl_checkmark.config(text=marks)
        if reps > 8:
            marks = ""
            lbl_checkmark.config(text=marks)
            reps = 1


# ---------------------------- UI SETUP ------------------------------- #
window = tk.Tk()
window.title("Pomodoro")
#window.minsize(width=500, height=400)
window.config(padx=100, pady=50, bg=YELLOW)

canvas = tk.Canvas(window, width=200, height=224, bg=YELLOW, highlightthickness=0)
try:
    tomato_img = tk.PhotoImage(file=resource_path("tomato.png"))
except tk.TclError:
    tomato_img = tk.PhotoImage(file="./pomodoro_app/tomato.png")

canvas.create_image(100, 112, image=tomato_img)
canvas.grid(row=1, column=1)


btn_start = tk.Button(window, text="Start", command=start_timer, height=0, width=10)
btn_start.grid(row=2, column=0)


btn_reset = tk.Button(window, text="Reset", command=reset_timer, height=0, width=10)
btn_reset.grid(row=2, column=2)

lbl_title = tk.Label(window, text="Timer", fg=GREEN, font=(FONT_NAME, 50, "bold"))
lbl_title.grid(row=0, column=1)
lbl_title.config(padx=0, pady=0, bg=YELLOW)

timer_text = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME,35,"bold"))
lbl_checkmark = tk.Label(window, text="", fg=GREEN, font=(FONT_NAME, 14, "bold"), bg=YELLOW)
lbl_checkmark.grid(row=3, column=1)

window.mainloop()