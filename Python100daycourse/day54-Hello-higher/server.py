from flask import Flask
from random import randint

app = Flask(__name__)



@app.route("/")
def home():
   global number_to_guess
   number_to_guess = randint(0,9) 
   return "<h1>Guess a number between 0 and 9</h1>" + \
          "<img src='https://media.giphy.com/media/3o7aCSPqXE5C6T8tBC/giphy.gif' width='300' height='300'>"

@app.route("/<int:number>")
def user_guess(number):
    if number > number_to_guess:
        return "<h1 style='color:red'>Too high! Try again</h1>" + \
          "<img src='https://media.giphy.com/media/3o6ZtaO9BZHcOjmErm/giphy.gif' width='300' height='300'>"
    elif number < number_to_guess:
        return "<h1 style='color:purple'>Too low! Try again</h1>" + \
          "<img src='https://media.giphy.com/media/jD4DwBtqPXRXa/giphy.gif' width='300' height='300'>"
    else:
        return "<h1 style='color:green'>You found me!</h1>" + \
          "<img src='https://media.giphy.com/media/4T7e4DmcrP9du/giphy.gif' width='300' height='300'>"


if __name__ == "__main__":
    app.run(debug=True)