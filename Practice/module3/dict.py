# Dictionaries are mutable
language = {}
# We can add properties after we created a dictionary
language = {"name": "Python", "version": 3.9}
language["website"] = "https://www.python.org"
language["file_extension"] = ".py"

file_extension = language.get("file_extension", 
                              "No file extension found")

print(language["name"], language["version"], language["website"],
      file_extension)  # Output: Python 3.9 https://www.python.org   .py
