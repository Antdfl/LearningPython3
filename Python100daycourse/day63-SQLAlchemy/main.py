from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from pathlib import Path
import os

cls = os.system('cls' if os.name == 'nt' else 'clear')

db_path = Path(__file__).parent / "new-books-collection.db"
print(db_path)                        # prints the full path to the database file

app = Flask(__name__)

# First Define a base class for the models using SQLAlchemy's DeclarativeBase
class Base(DeclarativeBase):
    pass

# Second step is to create an instance of the SQLAlchemy class, which will be used to interact with the database.
db = SQLAlchemy(model_class=Base)

# Third step is to set the URI for the database, which is a string 
# that tells SQLAlchemy where the database is located and how to connect to it.
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# Fourth step is to initialize the SQLAlchemy instance with the Flask application, 
# which allows SQLAlchemy to work with the Flask app and manage the database connection.
db.init_app(app)

# Subclass db.Model to create a model class. Unlike plain SQLAlchemy, 
# Flask-SQLAlchemy’s model will automatically generate a table name 
# if __tablename__ is not set and a primary key column is defined.
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250),nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'



# To add a new book to the database, we create an instance of the Book 
# model and add it to the session, then commit the session to save the changes to the database.
# In the CRUD, the step below is the Create (Insert)
# with app.app_context():
#     new_book = Book(title='Harry Potter', author='J. K. Rowling', rating=9.3)
#     db.session.add(new_book)
#     db.session.commit()

#Read All Records
# with app.app_context():
#     # result contains the all the record set, meaning all the record from our query
#     result = db.session.execute(db.select(Book).order_by(Book.title))
#     all_books = result.scalars().all()   # ← .all() materialises the list immediately
  
# for book in all_books:
#     print(f" {book.id} {book.title} {book.author} {book.rating}")

#Read A Particular Record By Query
# with app.app_context():
#     book = db.session.execute(db.select(Book).where(Book.title == "Harry Potter")).scalar()
# #To get a single element we can use scalar() instead of scalars().#

# print(f"Book {book.id} {book.title} {book.author} {book.rating}")

#Update A Particular Record By Query
# with app.app_context():
#     book_to_update = db.session.execute(db.select(Book).where(Book.title == "Harry Potter")).scalar()
#     book_to_update.title = "Harry Potter and the Chamber of Secrets"
#     db.session.commit()

# with app.app_context():
#     book = db.session.execute(db.select(Book).where(Book.id == 1)).scalar()
#     #To get a single element we can use scalar() instead of scalars().#
# print(f"Book {book.id} {book.title} {book.author} {book.rating}")

#Update A Record By PRIMARY KEY
# book_id = 1
# with app.app_context():
#     book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
#     # or book_to_update = db.get_or_404(Book, book_id)  
#     book_to_update.title = "Harry Potter and the Goblet of Fire"
#     db.session.commit()  

# with app.app_context():
#     book = db.session.execute(db.select(Book).where(Book.id == 1)).scalar()
#     #To get a single element we can use scalar() instead of scalars().#
# print(f"Book {book.id} {book.title} {book.author} {book.rating}")

#Delete A Particular Record By PRIMARY KEY
book_id = 1
with app.app_context():
    book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    # or book_to_delete = db.get_or_404(Book, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()

# with app.app_context():
#     book = db.session.execute(db.select(Book).where(Book.id == 1)).scalar()
#     #To get a single element we can use scalar() instead of scalars().#
# print(f"Book {book.id} {book.title} {book.author} {book.rating}")