# my_list =[1,2,3]
# for v in range(len(my_list)):
#      my_list.insert(1,my_list[v])
# print(my_list)

# val = [0,1,2]
# val.insert(0,1)
# del val[1]
# print(val)

# var=1
# while var<10:
#      print("#")
#      var= var << 1
#      print(var)

# my_list = [3,1,-2]
# print(my_list[my_list[-1]])

# a=1
# b=0
# c=a&b
# d=a|b
# e=a^b
# print(c)
# print(d)
# print(e)
# print(c+d+e)

# def subtra(a, b):
#     print(a - b)

# subtra(5, b=2)    # outputs: 3
# subtra(a=5, 2)    # Syntax Error

# def add_numbers(a, b, c=0):
#     print(a + b + c)

# add_numbers(a=1, b=3)

def is_leap_year(year):
     if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
          return True
     else:
          return False

# Example usage:
year = int(input("Enter a year: "))
if is_leap_year(year):
     print(f"{year} is a leap year.")
else:
     print(f"{year} is a common year.")