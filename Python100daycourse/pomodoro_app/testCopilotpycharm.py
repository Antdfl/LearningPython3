# Import th os module and use to clear screen at the start of the program
import os
os.system('cls' if os.name == 'nt' else 'clear')

# Simple loop to demonstrate functionality
# for i in range(10):
#  # Values in the loop body such as printing will be suggested by Copilot
#     print(f"Iteration {i}")
#
# print("Loop completed.")

# function that returns a prime number
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# test the is_prime function
for num in range(20):
    if is_prime(num):
        print(f"{num} is a prime number.")
    else:
        print(f"{num} is not a prime number.")