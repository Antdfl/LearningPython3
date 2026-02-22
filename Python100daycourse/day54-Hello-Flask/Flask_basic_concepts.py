import os
import time
# Clear the console so output is clean when the script is run.
# 'cls' is the Windows command; 'clear' is the Unix/macOS equivalent.
os.system('cls' if os.name == 'nt' else 'clear')

# This example explains two important concepts in Python:
# 1.First-class functions: Functions can be treated like any other object (assigned to variables, passed as arguments, returned from other functions).

# def add(n1, n2):
#     """A simple function that takes two numbers and returns their sum."""
#     return n1 + n2

# def subtract(n1, n2):
#     """A simple function that takes two numbers and returns their difference."""
#     return n1 - n2  

# def calculate(n1, n2, operation):
#     """A function that takes two numbers and an operation function, then applies the operation."""
#     return operation(n1, n2)

# 2.Nested functions: Functions can be defined inside other functions, creating a local scope for the inner function.

# ── CONCEPT 1: Nested functions (commented out for reference) ──────────────────
# In Python, functions can be defined inside other functions.
# The inner function is only accessible within the scope of the outer function —
# it cannot be called directly from outside.
# In this example, outer_function() defines and immediately calls inner_function().

# def outer_function():
#     print("This is the outer function.")

#     def inner_function():
#         print("This is the inner function.")

#     inner_function()   # inner_function is called here, inside the outer function

# outer_function()   # Calling outer triggers both prints

# ── CONCEPT 2: Functions as return values (first-class functions) ──────────────
# In Python, functions are "first-class objects", meaning they can be:
#   - Assigned to variables
#   - Passed as arguments
#   - Returned from other functions
#
# This is the foundation for Python decorators (used heavily in Flask, e.g. @app.route).
# Here, outer_function does NOT call inner_function — it returns it as an object.
# def outer_function():
#     print("This is the outer function.")

#     def inner_function():
#         print("This is the inner function.")

#     # Return the function object itself (no parentheses = no call, just a reference).
#     return inner_function

# # outer_function() runs and prints "This is the outer function."
# # Its return value — the inner_function object — is stored in the variable.
# inner_function = outer_function()

# # Now we call the returned function by adding parentheses.
# # Without the parentheses, inner_function would just be a reference to the function,
# # not an execution of it.
# inner_function()

# In Flask, this concept is used when we define routes with @app.route.
# The decorator @app.route("/") is essentially a function that takes another function (the view function) as an argument and modifies its behavior (e.g., by registering it as a route handler).
# So we can better explain the concept of Python decorators in the context of Flask, which is a web framework that allows us to create web applications easily.

# So the decorator takes a function as an argument, 
# defines a wrapper function that calls the original function, 
# and then returns the wrapper function. 
# This allows us to add functionality to the original function without modifying its code directly. 
# In Flask, this is how we can define routes and add functionality to our view functions using decorators.

 # Python Decorator
def delay_decorator(function):
    def wrapper_function():
        time.sleep(2)
        # Do something before
        function() # call the original
        function() # run the function twice
        # Do something after
    return wrapper_function

@delay_decorator
def say_hello():
    print("Hello!")

@delay_decorator
def say_goodbye():
    print("Goodbye!")

def say_greeting():
    print("How are you doing today?")

# I want to add a prespecified delay time before executing the say_hello function, without modifying its code directly.
# say_hello()
# say_greeting()

decorated_function = delay_decorator(say_greeting) # This is how the decorator works under the hood
decorated_function() # This is how we would call the decorated function without using the @ syntax