# Seven-segment display patterns for digits 0-9 (13 LEDs, 3 columns x 5 rows)
digits = {
    '0': [
        "###",
        "# #",
        "# #",
        "# #",
        "###"
    ],
    '1': [
        "  #",
        "  #",
        "  #",
        "  #",
        "  #"
    ],
    '2': [
        "###",
        "  #",
        "###",
        "#  ",
        "###"
    ],
    '3': [
        "###",
        "  #",
        "###",
        "  #",
        "###"
    ],
    '4': [
        "# #",
        "# #",
        "###",
        "  #",
        "  #"
    ],
    '5': [
        "###",
        "#  ",
        "###",
        "  #",
        "###"
    ],
    '6': [
        "###",
        "#  ",
        "###",
        "# #",
        "###"
    ],
    '7': [
        "###",
        "  #",
        "  #",
        "  #",
        "  #"
    ],
    '8': [
        "###",
        "# #",
        "###",
        "# #",
        "###"
    ],
    '9': [
        "###",
        "# #",
        "###",
        "  #",
        "###"
    ]
}

# def display_digit(digit):
#     pattern = digits.get(digit, ["   "] * 5)
#     for line in pattern:
#         print(line)

# I need a function that take in input and display the corresponding digit pattern
def print_number(number):
    for row in range(5):
        line = ""
        for digit in number:
            pattern = digits.get(digit, ["   "] * 5)
            line += pattern[row] + " "
        print(line)

# Example usage:
num = input("Enter a number (123): ")
print_number(num)
# Example usage:
# num = input("Enter a digit (0-9): ")
