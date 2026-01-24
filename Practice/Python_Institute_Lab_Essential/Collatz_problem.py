c0 = int(input("Type a number: "))
i=0
if c0 <0 or c0==1:
    print("The number should be a natural greater than 0 and not equal 1")
else:
    while c0 != 1 and c0 > 0:
         i += 1
        #  print("Start loop c0 :",c0)
         if (c0%2) == 0: # even
             c0 = c0/2
         else:
             c0 = 3*c0+1
         print("c0 :",int(c0))
        #  if i > 10:
        #       break
print("steps:", i)