total = 0
while input("Continue? (Y/n) ")=="Y":
    qty = int(input("Enter quantity: "))
    if qty < 0: 
        break
    total += qty
print("The total quantity is", total)