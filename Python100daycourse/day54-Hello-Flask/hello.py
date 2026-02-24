from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<h1 style='text-align:center'>Hello, World!</h1>" \
    "<p>This is a paragraph.</p>" \
    "<img src='https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDU3YnJjdzdvMXZ3YWpmMm1oaTlxeXM1a2ViN2VpeHRmNHU0MDQyeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kvrvnB158J4fm/giphy.gif'" \
    " alt='Two kittens playfully interact with each other.' width='500'>"

def make_bold(function):
    def wrapper_function():
        return "<b>" + function() + "</b>"
    return wrapper_function

def make_emphasis(function):
    def wrapper_function():
        return "<em>" + function() + "</em>"
    return wrapper_function

def make_underlined(function):
    def wrapper_function():
        return "<u>" + function() + "</u>"
    return wrapper_function


@app.route("/bye")
@make_bold
#@make_emphasis
#@make_underlined
def say_goodbye():
    return "<p>Goodbye!</p>"

#@app.route("/username/<path:name>")
@app.route("/username/<name>/<int:number>")
def greet(name, number):
    return f"Hello there, {name.capitalize()}! You are {number} years old."



if __name__ == "__main__":
    app.run(debug=True)
