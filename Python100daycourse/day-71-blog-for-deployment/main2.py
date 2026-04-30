import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, inspect

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'reset-key'

uri = (os.environ.get('POSTGRES_URI')
       or os.environ.get('SQLALCHEMY_DATABASE_URI')
       or os.environ.get('DATABASE_URL')
       or os.environ.get('DB_URI'))

if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

if not uri:
    uri = 'sqlite:///./instance/posts.db'

app.config['SQLALCHEMY_DATABASE_URI'] = uri

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")

with app.app_context():
    db.drop_all()
    db.create_all()
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('users')]

@app.route('/')
def index():
    db_type = 'PostgreSQL' if 'postgresql' in uri else 'SQLite'
    safe_uri = uri.split('@')[-1] if '@' in uri else uri
    return (f'<h2>Database: {db_type}</h2>'
            f'<p>Host/path: {safe_uri}</p>'
            f'<p>Colonne tabella users: {columns}</p>'
            f'<p>Se vedi postgresql e email nelle colonne, ora ripristina main.py originale.</p>')
