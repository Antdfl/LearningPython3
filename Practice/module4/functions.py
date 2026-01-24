
# rect_length = 10
# rect_width = 5

# rect_area = rect_length * rect_width
# print("Area of the Rectangle", rect_area)

# circle_radius = 12
# pi = 3.14159

# circle_area = pi * circle_radius ** 2
# print("Area of the Circle", circle_area)

def calculate_rectangle_area(length, width):
    return length * width

def calculate_circle_area(radius):
    pi = 3.14159
    return pi * radius ** 2

print("Area of the Rectangle", calculate_rectangle_area(10, 5))
print("Area of the Circle", calculate_circle_area(12))