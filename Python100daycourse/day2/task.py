print("Welcome to the tip calculator!")
bill = float(input("What was the total bill? $"))
tip = int(input("What percentage tip would you like to give? 10 12 14 "))
people = int(input("How many people to split the bill? "))
tip_percent = tip / 100
total_tip_amount = bill * tip_percent
total_bill = round(bill + total_tip_amount,2)
BillPerPerson = round(total_bill/people,2)
print(f"Each person should pay is {BillPerPerson} dollars per person")



