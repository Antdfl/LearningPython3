# import os
# os.system('cls' if os.name == 'nt' else 'clear')

countries = ["USA", "Canada", "Mexico"]

countries.append("Brazil")  # Add Brazil to the list
countries.insert(0, "Argentina")  # Insert Argentina at index 0
# countries.remove("Mexico")  # Remove Mexico from the list
#brazil = countries.pop(1)  # Remove the last item and store it in brazil
print(len(countries))  # Output: 3

print(countries)
# print(countries[-1])
# print(countries[-2])
# countries.sort()
# print(countries)

#countries.reverse()
countries.sort(reverse=True)
print(countries)
