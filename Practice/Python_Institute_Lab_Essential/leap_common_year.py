year = int(input("Enter a year: "))

if year < 1852:
    print("Not within the Gregorian calendar period")
else:    
    if (year%4) != 0:
        print("Common Year")
    else:
        print("Leap Year")

 
    
	
