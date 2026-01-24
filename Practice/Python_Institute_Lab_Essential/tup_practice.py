# tup = 1, 2, 3, 2, 4, 5, 6, 2, 7, 2, 8, 9
# duplicates = 0
# for i in range(len(tup)):
#     # print(tup[i], tup.count(tup[i]))
#     if tup.count(tup[i]) > 1:
#         duplicates += 1
# print(duplicates)    # outputs: 4

# d1 = {'Adam Smith': 'A', 'Judy Paxton': 'B+'}
# d2 = {'Mary Louis': 'A', 'Patrick White': 'C'}
# d3 = {}

# for item in (d1, d2):
#     d3.update(item)

# print(d3)

# my_list = ["car", "Ford", "flower", "Tulip"]

# t = tuple(my_list)
# print(t)

colors = (("green", "#008000"), ("blue", "#0000FF"))

# Write your code here.
colors_dictionary = dict(colors)

print(colors_dictionary)