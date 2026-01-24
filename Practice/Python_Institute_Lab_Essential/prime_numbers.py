def is_prime(num):
    if ((num == 2 or num == 3 or num ==5 or num==1)
            or not(num%2==0 or num%3==0 or num%5==0 or num%7==0)):
        return True
    else:
        return False

for i in range(1, 120):
    if is_prime(i):
	    print(i,end=" ")
print()
