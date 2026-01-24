# def printName():
#     global name
#     name = name + "!"
#     print(name)

# name = input("Enter your name: ")  # global variable
# printName()

def printMixed(a, b, *data, **person):
    print("a:", a)
    print("b:", b)
    print("data:", data)
    print("person:", person)

printMixed(2, 3, 4, 5, 5, 5, 6, 7, name="Max")

# def printData(*data):
#     print(type(data))

# printData(1, 3, "string", True, [2, 3])

# def printPerson(**person):
#     print(person["name"], end=".")

# printPerson(name="Eva", age=23, email="eva@gmail.com")

# def printData(*data):
#     print(type(data))


# printData(1, 3, "string", True, [2, 3])
