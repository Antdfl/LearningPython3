import os
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_screen()

# try:
#     print("-----------")
#     number = int(input("Enter a number: "))
#     try:
#         result = 10 / number
#     except ZeroDivisionError:
#         print("Sorry we can't divide by zero")
#     else:
#         print("The result is", result)
# except ValueError:
#    print("Oups! It didn't work, that's not a number")
# except KeyboardInterrupt:
#     print("You pressed Ctrl-C")
# else: 
#     print("Your number is", number)
# finally:
#     print("End of program")

# def calculate_discount(price, discount_rate):
#     if discount_rate<0:
#         raise ValueError("Discount rates should be > 0")
# calculate_discount(100, -1)

print((5 * ((25 % 13) + 100) / (2 * 13)) // 2)
print(25 % 13)
print((2 % -4), (2 % 4), (2 ** 3 ** 2))
print(2**9)