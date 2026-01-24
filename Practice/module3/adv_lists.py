countries = ['Argentina', 'Brazil', 'Canada',
              'Denmark', 'Estonia', 'Zambia']
# print("First time: "+str(countries)) 

# .copy create a copy of the list
# without affecting the original list
# new_countries = countries.copy()
# new_countries.append('Finland')

# This is another way to create a copy
# new_countries2 = countries[:]
# new_countries2.append('France')
# print("Original list: "+str(countries))
# print("Modified list: "+str(new_countries))
# print("Modified list 2: "+str(new_countries2))

# matrix =[[1,2],[3,4],[5,6]]
# Print the first row of the matrix
# print("First row of the matrix: "+str(matrix[0]))
# # Print the second element of the first row
# print("Second element of the first row: "+str(matrix[0][1]))
# print("Last element of the first row: "+str(matrix[0][-1]))
# # Print the last row of the matrix
# print("Last row of the matrix: "+str(matrix[-1]))
# # Print the last element of the last row
# print("Last element of the last row:"+str(matrix[-1][-1]))

numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
comprehension = [x*2 for x in numbers]
print(comprehension)

# This is similar to map in another language
print([c+":" for c in countries])

numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
comprehension = [x*2 for x in numbers if x<5]
print(comprehension)

print([c+":" for c in countries if len(c) > 6])