from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from pathlib import Path
import os

app = Flask(__name__)

all_books = []

# DB Setup
db_path = Path(__file__).parent / "new-books-collection.db"
print(db_path) 
# First Define a base class for the models using SQLAlchemy's DeclarativeBase
class Base(DeclarativeBase):
    pass
# Second step is to set the URI for the database, which is a string 
# that tells SQLAlchemy where the database is located and how to connect to it.
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
#  Third step is to create an instance of the SQLAlchemy class, which will be used to interact with the database.
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250),nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'
# Finally, we create the database tables based on the defined models.   
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    results = db.session.execute(db.select(Book).order_by(Book.title)).scalars()
    all_books = results.all()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        new_book = Book(
            title = request.form["title"],
            author= request.form["author"],
            rating=float(request.form["rating"])
        )
        db.session.add(new_book)
        db.session.commit()
        #print(all_books)
        return redirect(url_for("home"))
    return render_template("add.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        book_id = request.form["id"]
        book_to_update = db.get_or_404(Book, book_id)
        book_to_update.rating = float(request.form["rating"])
        db.session.commit()
        return redirect(url_for("home"))
    book_id = request.args.get("id")
    book_selected = db.get_or_404(Book, book_id)
    return render_template("edit_rating.html", book=book_selected)

@app.route("/delete")
def delete():
    book_id = request.args.get('id')
    # DELETE A RECORD BY ID
    book_to_delete = db.get_or_404(Book, book_id)
    # Alternative way to select the book to delete.
    # book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

