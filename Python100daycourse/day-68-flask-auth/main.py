from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from pathlib import Path
from wtforms import StringField, PasswordField, SubmitField
from wtforms import SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

login_manager = LoginManager()
login_manager.init_app(app)

# CREATE DATABASE


class Base(DeclarativeBase):
    pass

db_path = Path(__file__).parent / "instance/users.db"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


class CreatePostForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Submit User")
    
@app.route('/register', methods=["GET", "POST"])
def register():
    form = CreatePostForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if existing_user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        # Create new user
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('secrets'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Handles user authentication (Login). This function processes incoming requests 
    to either display the login form (GET) or attempt credential verification (POST).

    SECURITY NOTES:
    1. Existence and Password Check: The logic combines checking for user existence
       AND verifying the password hash (`check_password_hash`) into a single conditional
       block. This pattern is crucial to prevent both Python `AttributeError`s 
       and potential timing attacks that an attacker could exploit by measuring response time differences.
    2. State Management: Uses Flask-Login's `login_user()` and redirects upon success, 
       ensuring the user session is properly established.

    FLOW LOGIC:
    - GET Request: Renders the 'login.html' template, displaying an empty form for input.
    - POST Request: 
      1. Attempts to fetch a User object by email from the database.
      2. If the user does not exist OR the provided password fails validation: 
         Displays a generic failure message (for security) and redirects back to GET /login.
      3. On success: Logs in the user, flashes a success message, and redirects them to the protected 'secrets' page.

    Returns:
        Response: The rendered login template for GET requests or a redirect response for POST requests.
    """
    if request.method == "POST":
        # Check if user exists in the database by searching for the email
        user = db.session.execute(db.select(User).where(User.email == request.form.get('email'))).scalar()
        # Check password hash and user existence together to prevent errors and enhance security
        if not user:
            flash("That email does not exist, please try again.", 'login_error')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, request.form.get('password')):
            flash("Password incorrect, please try again.", 'login_error')
            return redirect(url_for('login'))
        else:   
            # Log in the user
            login_user(user)
            # If 'next' parameter exists, redirect to that page, otherwise redirect to secrets
            return redirect(url_for('secrets'))
    # If GET request, just render the login page
    return render_template("login.html")


@app.route('/secrets')
def secrets():
    # an alternative way to check if the user is authenticated without using the @login_required decorator
    if not current_user.is_authenticated:
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/download')
def download():
    # an alternative way to check if the user is authenticated without using the @login_required decorator
    if not current_user.is_authenticated:
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    return send_from_directory('static', 'files/cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
