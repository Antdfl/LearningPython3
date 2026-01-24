# (item_name, price_per_item, quantity)
items = [('apple', 0.5, 15), 
         ('banana', 0.25, 2), 
         ('grape', 0.75, 3)]  

total = 0
for item in items:
    total += item[1] * item[2]

if total > 10:
    discount = 0.1
    total_with_discount = total * (1 - discount)
else:
    total_with_discount = total

print("Total/Total after possible discount: ", total, total_with_discount)

