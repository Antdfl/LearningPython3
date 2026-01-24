total = 0
for number in range(0,6,2):
    price = input("Price for item " + 
                  str(number) + ": ")
    total += float(price)

print("The total to pay is", total)
