income = float(input("Enter the annual income: "))
# 
if income <= 85528:
   tax = (income*18/100)-556-0.02
   if tax < 0:
       tax = 0
else:
   tax=14839+0.02
   if income > 85528:
       tax = tax+(income-85528)*32/100
 
tax = round(tax, 0)
print("The tax is:", tax, "thalers")
