import os

cls = 'cls' if os.name == 'nt' else 'clear'
os.system(cls)
# Avanced Python decorators
# class User:
#     def __init__(self, name):
#         self.name = name
#         self.is_logged_in = False

# def is_authenticated_decorator(function):
#     def wrapper_function(*args, **kwargs):
#         if args[0].is_logged_in:
#             return function(args[0])
#         else:
#             print("User is not authenticated. Please log in.")
#     return wrapper_function

# @is_authenticated_decorator
# def create_blog_post_decorator(user):
#     print(f"Creating a blog post for the user {user.name}...")
    

# user = User("John")
# user.is_logged_in = True
# create_blog_post_decorator(user)

# TODO: Create the logging_decorator() function 👇
def logging_decorator(function):
    def wrapper_function(*args, **kwargs):
        result = function(*args, **kwargs)
        print(f"You called the {function.__name__} with args {args}\nIt returned: {result}")
        return result
    return wrapper_function

# @logging_decorator        # same as: a_function = logging_decorator(a_function)
# def a_function(*args):    # logging_decorator must return wrapper_function
#     return sum(args)      # so a_function becomes wrapper_function
# TODO: Use the decorator 👇
@logging_decorator
def a_function(*args):
    return sum(args)
    
a_function(1,2,3)
