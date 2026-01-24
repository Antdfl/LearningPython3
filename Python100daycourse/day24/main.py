import os
cwd = os.getcwd()
print(cwd)
from pathlib import Path
script_dir = Path(__file__).parent
print( script_dir)
file_path = script_dir / "myfile.txt"

# file = open(file_path, "r")
# contents = file.read()
# print(contents)
# file.close()

# with open(file_path, "w") as file:
#     file.write("\nHello, World!")
# C:\Users\ilpot\OneDrive\Desktop

with open("./Python100daycourse/day24/myfile.txt", "r") as file:
    contents = file.read()
    print(contents) 