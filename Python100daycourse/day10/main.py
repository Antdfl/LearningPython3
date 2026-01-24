from art import logo
print(logo)

def add(n1, n2):
    return n1 + n2

def subtract(n1,n2):
    return n1 - n2

def multiply(n1,n2):
    return n1 * n2

def divide(n1,n2):
    return n1 / n2

operations = {
	"+": add,
    "-" : subtract,
	"*" : multiply,
	"/": divide
}

#print(operations["*"](4,8))
should_continue = True
new_calculation = True
while should_continue:
    if new_calculation:
       first_number = float(input("What is the first number?: "))
    for symbol in operations:
        print(symbol)
    operation_symbol = input("Pick an operation: ")
    second_number = int(input("What is the next number?: "))
    operation_result = operations[operation_symbol](first_number, second_number)
    print(f"{first_number} {operation_symbol} {second_number} = {operation_result}")
    user_choice = input(f"Type 'y' to continue calculating with {operation_result}, or type 'n' to start a new calculation: ")
    if user_choice == "y":
        new_calculation = False
        first_number = operation_result
    else:
        new_calculation = True
        print("\n" * 20)
        print(logo)
    #should_continue =