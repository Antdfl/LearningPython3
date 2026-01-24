import os
os.system('cls' if os.name == 'nt' else 'clear')    

endOfProgram = False
while not endOfProgram:
    name = input("Name: ")
    if len(name)<2:
        endOfProgram = True
        continue
    else:
        age = int(input("Age: "))
        if age > 15:
            children = int(input("# Children: "))
            if (children>0):
                for c in range(children):
                    child_name = input("Child name: ")
        else:
            mother = input("Mother's Name:")

print("END.")
                
