# with open("./weather_data.csv") as data_file:
#     lines = data_file.readlines()
#     for line in lines:
#         print(line, end="")
# import csv
#
# with open("weather_data.csv") as data_file:
#     data = csv.reader(data_file)
#     temperatures = []
#     for row in data:
#         if row[1].isdigit():
#             temperatures.append(int(row[1]))
#     print(temperatures)
import pandas
from pandas import read_csv

data = pandas.read_csv("weather_data.csv")
#print(type(data))
#print(type(data["temp"]))
# data_dic = data.to_dict()
# print(data_dic)
# temp_list = data["temp"].tolist()
# print(temp_list)
# avg = round(sum(temp_list)/len(temp_list),2)
# print(data["temp"].mean())
#print(data.temp == data["temp"].max())
# print(data["condition"])
# print(data.condition)
#print(data[data.day == "Monday"])
#print(data[data.temp == data.temp.max()])
#monday = data[data.day == "Monday"]
# print(type(monday))
# print(type(monday.temp))
# print(monday.temp)
# temp_celsius = monday.temp[0]
# temp_fahrenheit = (temp_celsius * 9 / 5) + 32
# print(f"Temp Celsius {temp_celsius}, Temp Fahrenheit {temp_fahrenheit}")

# How to create a Dataframe from data that you have generated?
data_dict = {
    "students": ["Amy", "James", "Antonio"],
    "scores": [76, 56, 65]
}
df = pandas.DataFrame(data_dict)
print(df)
df.to_csv("new_data.csv")














