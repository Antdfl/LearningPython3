import colorgram

# Example: Extract colors from an image
#colors = colorgram.extract("image.jpg", 6)

# # Print the colors
# for color in colors:
#     print(color)

food = ["hamburger",  "orange", "pear", "kiwi", "ham","doughnut", "lettuce"]
healthy_food = ["orange","pear","kiwi", "lettuce" ]

if set(healthy_food).issubset(set(food)):
    print("Healthy food found!")
else:
    print("No healthy food found.")
