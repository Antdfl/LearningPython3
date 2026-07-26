"""
Movie Search Web Application using Flask and SQLAlchemy

This application allows users to search for movies by title or genre and retrieve movie data
(e.g., ratings). It uses a combination of database storage (SQLAlchemy) and external API calls
(via 'requests') to fetch real-world, up-to-date information.

SETUP INSTRUCTIONS:
------------------
1. Install Dependencies: Open the terminal in PyCharm and run the requirements file:
   python -m pip install -r day-64-top-movies/requirements.txt
2. Run the application: python main.py (or flask run)

NOTES ON FLASK COMPONENTS:
----------------------
- Flask-SQLAlchemy is used for persistent, structured data storage (e.g., saved movie data).
- WTForms handles all incoming user form data validation and processing.

SECURITY NOTE:
The database URI must be managed carefully in a production environment to prevent unauthorized access.
"""
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
# Using type hints for clarity: Mapped[Type] = mapped_column(...)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float # Includes all necessary SQL types
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired # Validator for required fields
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB


# CREATE TABLE


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
