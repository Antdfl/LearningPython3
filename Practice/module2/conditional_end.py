
try:
    price = input("What's the price? $")
    price = float(price)
    if price==0:
        print("You didn't enter a price")
    elif price<0:
        print("Invalid price")
    elif price<10:
        print("Discounted Price", "$", price*0.9)
    elif price<100:
        print("Increased Price. This price is for large orders  ", "$", price*1.2)
    else:
        print("Price", "$", price)
except Exception as e:
    print("An error occurred:", e)

print("End of program")
