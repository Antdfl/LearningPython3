"""
Python100daycourse/day-71-blog-for-deployment/main.py

Purpose: A Flask blog application with user authentication, CRUD operations
on blog posts, and per-post comments. Originally a 100 Days of Code
exercise, adapted here for deployment (environment-variable-driven
configuration, production database support via SQLAlchemy).

Audience Note for Junior Programmers:
This file uses several patterns that are easy to copy but hard to
understand from the code alone: Flask-Login's cookie/session-based
authentication flow, SQLAlchemy's declarative ORM with foreign keys and
relationships, and a custom route decorator for authorization. The
docstrings below focus on explaining *why* each piece works the way it
does, not just restating what the code already says.

Functionality Overview:
- Authentication: register/login/logout routes, password hashing (plain-
  text passwords are never stored), and a Flask-Login user_loader callback.
- Data model: BlogPost, User and Comment, linked through SQLAlchemy
  relationships (a user can have many posts and many comments; a post can
  have many comments).
- Authorization: an admin_only decorator restricts post creation/deletion
  to a single hardcoded admin user (id == 1).
- Blog CRUD: list/view/create/edit/delete posts, plus commenting on a post.

Dependencies (installed via requirements.txt): Flask, Flask-Bootstrap,
Flask-CKEditor, Flask-Login, Flask-SQLAlchemy, SQLAlchemy, Werkzeug
(password hashing), and WTForms (via the local forms module).
"""
import hashlib
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
import os
# from dotenv import load_dotenv
# load_dotenv()  # Remove for production
# Optional: add contact me email functionality (Day 60)
# import smtplib


'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_KEY',
    '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
)
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Reload a logged-in user from the database on every request.

    Flask-Login calls this automatically (registered via the
    @login_manager.user_loader decorator) to turn the user ID stored in the
    session cookie back into a real User object, making current_user
    available throughout the request.

    Args:
        user_id (str): The user's primary key, as stored in the session cookie.

    Returns:
        User: The matching user, or aborts with a 404 if none exists (via
            SQLAlchemy's get_or_404).
    """
    return db.get_or_404(User, user_id)


@app.errorhandler(404)
def page_not_found(e):
    """Handle HTTP 404 errors with a custom error page.

    Registered via @app.errorhandler(404), Flask calls this automatically
    instead of its default error page whenever a route or resource isn't
    found.

    Args:
        e: The exception object Flask passes to error handlers (unused
            here, since the page is static).

    Returns:
        tuple: The rendered '404.html' template and the HTTP status code 404.
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle HTTP 500 errors with a custom error page.

    Registered via @app.errorhandler(500), Flask calls this automatically
    for unhandled exceptions, showing a friendly page instead of a raw
    traceback to the user.

    Args:
        e: The exception object Flask passes to error handlers (unused
            here, since the page is static).

    Returns:
        tuple: The rendered '500.html' template and the HTTP status code 500.
    """
    return render_template('500.html'), 500


@app.template_filter('gravatar')
def gravatar_filter(email, size=100, rating='g', default='retro'):
    """Build a Gravatar avatar URL for a user's email address (a Jinja2 template filter).

    Gravatar identifies a user by the MD5 hash of their lowercased,
    whitespace-trimmed email address rather than the email itself, so it
    must be hashed before building the URL. Registered via
    @app.template_filter('gravatar'), so templates can call it as
    `{{ user.email | gravatar }}`.

    Args:
        email (str): The user's email address.
        size (int): Requested avatar size in pixels. Defaults to 100.
        rating (str): Gravatar content rating ('g', 'pg', 'r', 'x'). Defaults to 'g'.
        default (str): Fallback avatar style if the email has no Gravatar. Defaults to 'retro'.

    Returns:
        str: A complete Gravatar image URL.
    """
    hash_val = hashlib.md5(email.lower().strip().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_val}?s={size}&d={default}&r={rating}"

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

def get_database_uri():
    """Resolve the database connection URI from environment variables.

    Checks several common environment variable names, in order of
    preference, so the same code works across different hosting providers
    without changes. Some providers hand out URIs starting with
    'postgres://', which SQLAlchemy's newer psycopg driver rejects - those
    are rewritten to the 'postgresql://' prefix it expects. Falls back to a
    local SQLite file when no environment variable is set, so the app still
    runs during local development.

    Returns:
        str: A SQLAlchemy-compatible database connection URI.
    """
    env_keys = [
        'POSTGRES_URI',
        'DB_URI',
        'DATABASE_URL',
        'SQLALCHEMY_DATABASE_URI',
    ]
    for env_key in env_keys:
        uri = os.environ.get(env_key)
        if uri:
            if uri.startswith('postgres://'):
                uri = uri.replace('postgres://', 'postgresql://', 1)
            app.logger.warning('DB URI from %s: %s', env_key, uri.split('@')[-1])
            return uri
    app.logger.warning('No DB env var found, falling back to SQLite')
    return 'sqlite:///./instance/posts.db'

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'options': '-csearch_path=public'}}

db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    """SQLAlchemy model for a single blog post.

    Each post belongs to exactly one User (via author_id/author) and can
    have many Comments (via the comments relationship). back_populates
    keeps both sides of each relationship in sync automatically - setting
    `post.author` updates `user.posts` accordingly, and vice versa.
    """
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    # Parent relationship to the comments
    comments = relationship("Comment", back_populates="parent_post")


# Create a User table for all your registered users
class User(UserMixin, db.Model):
    """SQLAlchemy model for a registered user, and Flask-Login's session subject.

    Inherits from UserMixin, which supplies the properties Flask-Login
    expects (is_authenticated, is_active, get_id(), etc.), so this class
    can be used directly with login_user()/current_user. A user can author
    many BlogPosts and write many Comments, both modeled as one-to-many
    relationships.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    # This will act like a list of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")


# Create a table for the comments on the blog posts
class Comment(db.Model):
    """SQLAlchemy model for a comment left by a user on a blog post.

    Each comment belongs to exactly one User (comment_author) and exactly
    one BlogPost (parent_post) - two separate many-to-one relationships,
    not a single many-to-many one. Together they let a comment be traced
    back to both who wrote it and which post it's on.
    """
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # Child relationship:"users.id" The users refers to the tablename of the User class.
    # "comments" refers to the comments property in the User class.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the BlogPosts
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")


with app.app_context():
    db.create_all()


# Create an admin-only decorator
def admin_only(f):
    """Restrict a route to the admin user only (hardcoded as user id 1).

    Wraps a view function so it first checks current_user.id; anyone else
    gets a 403 Forbidden instead of the route running. @wraps(f) preserves
    the wrapped function's name/docstring, which Flask needs internally to
    tell routes apart.

    Args:
        f: The view function to protect.

    Returns:
        function: The wrapped view, enforcing the admin check before running f.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    """Handle new user sign-up: show the registration form, then create the account.

    On GET, just renders the empty form. On a valid POST, checks the email
    isn't already registered, hashes the password (never stored in plain
    text - see werkzeug's generate_password_hash), creates the User row,
    and logs the new user in immediately via Flask-Login's login_user().

    Returns:
        Response: The rendered registration form, or a redirect to the
            post list after a successful sign-up.
    """
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login: verify email/password and start a session.

    Looks up the user by email (unique in the database, so at most one
    match), then compares the submitted password against the stored hash
    with check_password_hash - the hash is one-way, so this is the only
    way to verify a password without ever storing or recovering the
    original.

    Returns:
        Response: The rendered login form (with a flash message on
            failure), or a redirect to the post list on success.
    """
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    """Log the current user out and redirect to the post list.

    Returns:
        Response: A redirect to the get_all_posts route.
    """
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    """Render the home page listing every blog post.

    Returns:
        str: The rendered index.html template with all posts passed in.
    """
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


# Add a POST method to be able to post comments
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    """Show a single blog post and handle new comments on it.

    On a valid comment submission, requires the visitor to be logged in
    (current_user.is_authenticated) before the comment is saved - the form
    itself doesn't enforce this.

    Args:
        post_id (int): The BlogPost's primary key, from the URL.

    Returns:
        str: The rendered post.html template with the post, its comments,
            and the comment form.
    """
    requested_post = db.get_or_404(BlogPost, post_id)
    # Add the CommentForm to the route
    comment_form = CommentForm()
    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


# Use a decorator so only an admin user can create new posts
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    """Create a new blog post (admin only, enforced by the @admin_only decorator).

    Returns:
        Response: The rendered post-creation form, or a redirect to the
            post list once the new post is saved.
    """
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


# Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    """Edit an existing blog post, pre-filling the form with its current values.

    Note this route has no @admin_only decorator, unlike add_new_post and
    delete_post - any logged-in user who reaches this URL can edit any post.

    Args:
        post_id (int): The BlogPost's primary key, from the URL.

    Returns:
        Response: The rendered form pre-filled with the post's data, or a
            redirect to the updated post once saved.
    """
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    """Delete a blog post (admin only, enforced by the @admin_only decorator).

    Args:
        post_id (int): The BlogPost's primary key, from the URL.

    Returns:
        Response: A redirect to the post list after deletion.
    """
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    """Render the static About page.

    Returns:
        str: The rendered about.html template.
    """
    return render_template("about.html", current_user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Render the static Contact page.

    Note: this route accepts POST as well as GET, but currently has no code
    to handle a POST submission - see the commented-out email-sending block
    further down in this file for how it was originally wired up (Day 60 of
    the course).

    Returns:
        str: The rendered contact.html template.
    """
    return render_template("contact.html", current_user=current_user)

# Optional: You can include the email sending code from Day 60:
# DON'T put your email and password here directly! The code will be visible when you upload to Github.
# Use environment variables instead (Day 35)

# MAIL_ADDRESS = os.environ.get("EMAIL_KEY")
# MAIL_APP_PW = os.environ.get("PASSWORD_KEY")

# @app.route("/contact", methods=["GET", "POST"])
# def contact():
#     if request.method == "POST":
#         data = request.form
#         send_email(data["name"], data["email"], data["phone"], data["message"])
#         return render_template("contact.html", msg_sent=True)
#     return render_template("contact.html", msg_sent=False)
#
#
# def send_email(name, email, phone, message):
#     email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
#     with smtplib.SMTP("smtp.gmail.com") as connection:
#         connection.starttls()
#         connection.login(MAIL_ADDRESS, MAIL_APP_PW)
#         connection.sendmail(MAIL_ADDRESS, MAIL_APP_PW, email_message)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
