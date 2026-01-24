def is_leap_year(year):
     if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
          return True
     else:
          return False

def days_in_month(year, month):
   if is_leap_year(year):
       month_list=[31,29,31,30,31,30,31,31,30,31,30,31]
   else:
       month_list=[31,28,31,30,31,30,31,31,30,31,30,31]
   if month >=1 and month <=12:
       return month_list[month-1]
   else:
       return None
  
# print("is_leap_year",is_leap_year(1900))    
test_years = [1900, 2000, 2016, 1987]
test_months = [2, 2, 1, 11]
test_results = [28, 29, 31, 30]
for i in range(len(test_years)):
	yr = test_years[i]
	mo = test_months[i]
	print(yr, mo, "->", end="")
	result = days_in_month(yr, mo)
# 	print("result","->",result)
	if result == test_results[i]:
		print("OK")
	else:
		print("Failed")
