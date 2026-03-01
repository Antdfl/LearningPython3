import sqlite3
from pathlib import Path
import os

cls = os.system('cls' if os.name == 'nt' else 'clear')

db_path = Path(__file__).parent / "books-collection.db"
print(db_path)                        # prints the full path to the database file
db = sqlite3.connect(db_path)         # sqlite3 accepts a Path object

cursor = db.cursor() # creates a cursor object to interact with the database

# cursor.execute("CREATE TABLE books " \
#       "(id INTEGER PRIMARY KEY, " \
#       "title varchar(250) NOT NULL UNIQUE, " \
#       "author varchar(250) NOT NULL, " \
#       "rating FLOAT NOT NULL)")                 # create a cursor object to interact with the database

cursor.execute("INSERT INTO books VALUES(1, 'Harry Potter', 'J. K. Rowling', '9.3')")
db.commit()
