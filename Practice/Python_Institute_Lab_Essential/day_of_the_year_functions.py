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

def day_of_year(year, month, day):
   num_day = 0
#   print(month)
   for i in range(month-1):
       i += 1
       days = days_in_month(year, i)
       if days is None:
           return None
       num_day += days
    #   print("i ->",i, days_in_month(year,i))
   num_day += day
   if num_day > 0:
       return num_day
   else:
       return None

print(day_of_year(2000, 12, 31))
