"""
main.py - Day 68: Flask Authentication Example (Python 100 Days Course)

Purpose: 
    This module implements a complete user authentication system using Flask, including 
    registration, login/logout functionality, protected routes, and file download handling.

Audience Note for Junior Programmers:
    This example demonstrates key security patterns in web development:
    - Password hashing with werkzeug.security to prevent plain-text password storage
    - Flask-Login integration for session management
    - Database-backed user persistence with SQLAlchemy
    
    Important security considerations:
    1. Passwords are never stored as plain text - they're hashed using PBKDF2-SHA256
    2. The SECRET_KEY is used by Flask-Login to sign cookies (in production, use a strong key)
    3. The database file is stored in the 'instance/' directory following Flask conventions

Functionality Overview:
    - User registration with email/password/name validation
    - Login with email/password verification
    - Protected routes that require authentication
    - Logout functionality
    - PDF file download from static/files/ directory

Dependencies:
    - flask: Web framework
    - flask_sqlalchemy: SQLAlchemy integration for ORM
    - flask_login: User session management
    - wtforms: Form validation
    - werkzeug.security: Password hashing utilities
"""

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
    """
    SQLAlchemy ORM model representing a registered user in the database.

    This model defines the structure of the users table with fields for email, password hash,
    and display name. The email field is unique to prevent duplicate registrations. Passwords
    are stored as hashed values (never plain text) for security - see werkzeug.security module.

    Table: users

    Fields:
        id (int): Primary key, auto-incrementing unique identifier for each user.
        email (str): User's email address (unique, max 100 characters). Used for login.
        password (str): Hashed password (max 100 characters). Never stored in plain text.
        name (str): Display name for the user (max 1000 characters).

    Usage:
        - Create a new user: User(email='...', password=hashed_password, name='...')
        - Fetch by ID: db.session.get(User, user_id)
        - Fetch by email: db.session.execute(db.select(User).where(User.email == '...'))
    """
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


@login_manager.user_loader
def load_user(user_id):
    """
    Callback function used by Flask-Login to retrieve a user object from the database.

    This function is automatically invoked when Flask-Login needs to verify or load
    a user during session management (e.g., when checking authentication on protected routes).
    The @login_manager.user_loader decorator registers this function as the loader for
    users identified by their numeric ID stored in the session cookie.

    Parameters:
        user_id (int): The numeric ID of the user to retrieve from the database. This
            value comes from the Flask-Login session and represents the primary key
            (id) of a User record.

    Returns:
        User or None: The User object if found in the database, None otherwise. Returning
        None will cause Flask-Login to deny access to the protected route.
    """
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    """
    Displays the main home page of the application.

    This route serves as the landing page when users navigate to the root URL (/).
    It renders the 'index.html' template which typically contains:
    - A welcome message
    - Navigation links to login/registration pages
    - Possibly a summary of available features or recent posts (if implemented)

    Returns:
        Response: Renders the index.html template with default context. The template
        should include navigation for authenticated and unauthenticated users,
        as well as any introductory content appropriate for the application's purpose.
    """
    return render_template("index.html")


class CreatePostForm(FlaskForm):
    """
    WTForms form for user registration.

    This form collects user information required during the registration process:
    - Name: The user's display name (required)
    - Email: The user's email address (required, validated as a valid email format)
    - Password: The user's password (required, minimum 6 characters)
    - Submit: Form submission button

    Usage:
        - Instantiate the form in a view function: form = CreatePostForm()
        - Validate the form data: if form.validate_on_submit(): ...
        - Access form fields via form.<field_name>.data (e.g., form.email.data)
    """
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Submit User")
    
@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Handles user registration. This function processes incoming requests to either display
    the registration form (GET) or create a new user account (POST).

    FLOW LOGIC:
    - GET Request: Instantiates an empty CreatePostForm and renders 'register.html'.
    - POST Request: 
      1. Validates the form data (email, password, name).
      2. Checks if a user with the same email already exists in the database.
         If so, flashes an error message and redirects to login.
      3. Hashes the provided password using PBKDF2-SHA256 algorithm.
      4. Creates a new User record with the form data and hashed password.
      5. Commits the new user to the database.
      6. Logs in the newly created user automatically (sets session cookie).
      7. Redirects to the 'secrets' page (protected route).

    SECURITY NOTE:
        New users are logged in immediately after registration. This is a common pattern
        to give new users direct access to their dashboard without requiring an additional
        login step. The user's session cookie is set automatically via login_user().

    Returns:
        Response: The 'register.html' template for GET requests, or a redirect 
        response pointing to url_for('secrets') after successful registration.
    """
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
    """
    Displays a secret/public message page for authenticated users.

    This route serves as an example of manual authentication checking, implemented as
    an alternative to Flask-Login's @login_required decorator. While @login_required
    automatically protects entire route blocks, this pattern allows per-route control
    over what messages or context is shown when a user is not authenticated.

    FLOW LOGIC:
        1. Check if current_user.is_authenticated returns False via manual inspection.
        2. If unauthenticated: Flash a warning message and redirect to /login.
        3. If authenticated: Render 'secrets.html' template with any needed context.

    SECURITY NOTE:
        This demonstrates the same authentication check as @login_required, but written
        inline for educational purposes. In production code, prefer decorators or
        access control libraries (e.g., Flask-Talisman) to reduce repetitive manual checks.

    Returns:
        Response: Renders secrets.html if authenticated, otherwise redirects to login with a flash message.
    """
    # an alternative way to check if the user is authenticated without using the @login_required decorator
    if not current_user.is_authenticated:
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    """
    Logs out the currently authenticated user and redirects to the home page.

    This route handles user logout by invalidating the session cookie that Flask-Login
    sets upon login. After logout, users are redirected back to the main home page (/).

    FLOW LOGIC:
        1. Calls logout_user() from Flask-Login to clear the current user's session data.
        2. Flashes a confirmation message indicating successful logout.
        3. Redirects the user to the home route via url_for('home').

    Returns:
        Response: A redirect response pointing to the home page after logout.
    """
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/download')
def download():
    """
    Serves a PDF file from the static/files/ directory after verifying authentication.

    This route demonstrates manual authentication checking as an alternative to using
    the @login_required decorator. The function handles both authenticated and 
    unauthenticated users with different responses.

    FLOW LOGIC:
        1. Check if current_user.is_authenticated returns False via manual inspection.
        2. If unauthenticated: Flash a warning message and redirect to /login page.
        3. If authenticated: Serve the file 'static/files/cheat_sheet.pdf' using 
           send_from_directory().

    SECURITY NOTE:
        This pattern demonstrates how to manually guard specific resources (like files)
        behind authentication checks. In production, consider using @login_required for
        consistent protection across multiple routes or Flask-Talisman for broader security.

    Returns:
        Response: Either an HTML redirect to login with a flash message (if not authenticated),
           or sends the PDF file response if authenticated. The send_from_directory function
           handles setting appropriate Content-Type headers for the PDF file.
    """
    # an alternative way to check if the user is authenticated without using the @login_required decorator
    if not current_user.is_authenticated:
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    return send_from_directory('static', 'files/cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
