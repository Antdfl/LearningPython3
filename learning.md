# Python Learning Progress

---

## Python Institute – PCAP Certification Preparation

### Modules and Packages

- Python module system: `import`, `from … import`, aliasing with `as`
- `sys.path` – how the interpreter searches for modules; inspecting with `sys.path`
- Creating reusable modules: functions, private variables (`__counter`), module-level state
- `if __name__ == "__main__"` guard for self-testing modules
- Package structure: `__init__.py`, directory hierarchy as namespace
- Nested packages (4-level deep: `extra → good → best → sigma/tau`)
- Importing from nested packages: `from extra.good.best.sigma import FunS`

### String Algorithms and Data Structures

- Caesar cipher: character-by-character transformation, ASCII arithmetic (`ord()`, `chr()`)
- Wrap-around logic using modulo: `(ord(c) - ord('A') + shift) % 26`
- Filtering non-alphabetic characters, normalising case
- IBAN validation algorithm:
  - Input sanitisation (remove spaces, check alphanumeric)
  - Length constraints (15–31 characters)
  - Rearranging: move last 4 chars to front
  - Letter-to-number conversion (A=10 … Z=35)
  - Modulo 97 validation
- Seven-segment display: dictionary of digit → list-of-row-strings pattern
- Building visual output by iterating rows across multiple digits

### GUI Basics with Pygame

- `pygame.init()`, display surface creation (`pygame.display.set_mode()`)
- Event loop: `pygame.event.get()`, handling `QUIT`, `MOUSEBUTTONDOWN`, `KEYDOWN`
- Font rendering: `pygame.font.SysFont()`, `font.render()`, `surface.get_rect(center=…)`
- Drawing text centred on screen, `pygame.display.flip()`

---

## Python Institute – Certified Entry-Level Python Programmer (PCEP)

### 1. Computer Programming and Python Fundamentals

- Fundamentals of Python – interpreter, compilation vs interpretation
- Writing and executing Python code, Python code structure
- PEP8 style guidelines and indentation rules
- Variables, literals, and naming conventions
- Output to console (`print()`), input from console (`input()`)
- Numerical representations: integers, floats, scientific notation
- String operations: concatenation, indexing, slicing, methods
- Type casting between int, float, str

### 2. Control Flow: Conditional Blocks and Loops

- `if`, `elif`, `else` conditional blocks
- `while` loop with conditions and accumulators
- `for` loop with `range()` and iterables
- Loop control: `break`, `continue`
- `else` clause with loops
- Nesting loops and conditions

### 3. Data Collections: Lists, Tuples, Dictionaries

- Lists: creation, indexing, slicing, mutability
- List methods: `append()`, `insert()`, `remove()`, `pop()`, `sort()`, `reverse()`
- Tuples: immutability, use cases, unpacking
- Dictionaries: key-value pairs, access, update, deletion
- Iterating through dictionaries (`.keys()`, `.values()`, `.items()`)
- Mixing collections: lists of dicts, dicts of lists

### 4. Functions and Exceptions

- Defining functions with `def`, `return` values
- Positional and keyword arguments, default parameter values
- Variable scope: local vs global
- Generators and `yield`
- `try`, `except`, `else`, `finally` blocks
- Raising exceptions with `raise`
- Built-in exception types: `ValueError`, `TypeError`, `KeyError`, `IndexError`

---

## 100 Days of Code Bootcamp (Angela Yu – Udemy)

### Days 1–19: Python Fundamentals and OOP Basics

- Input/output, string manipulation, type conversion
- Conditionals and loops in practical projects
- Functions, scope, default arguments
- Object-oriented programming: classes, objects, attributes, methods
- Inheritance and method overriding
- `__init__` constructor, `self` reference
- Turtle graphics library for OOP game projects (Snake, Pong, Frogger-style)

### Days 24–25: File I/O and Pandas

- Reading and writing `.txt` and `.csv` files
- `with open()` context manager, file modes (`r`, `w`, `a`)
- `pandas` library: `DataFrame`, `Series`, reading CSVs
- DataFrame filtering, column operations, iterating rows
- Project: US States guessing game (pandas + Turtle)
- Mail Merge: file I/O to generate personalised letters from a template

### Day 29: GUI with Tkinter

- Tkinter widget types: `Label`, `Entry`, `Button`, `Text`, `Canvas`
- Layout managers: `pack()`, `grid()`, `place()`
- Event binding and callbacks
- JSON file storage for persistence (`json.load()`, `json.dump()`)
- `pyperclip` for clipboard integration
- Project: Password Manager with random password generation and JSON storage

### Days 33–40: APIs, Web Scraping, and Automation

- HTTP request methods: GET, POST, understanding status codes
- `requests` library: `.get()`, `.post()`, `.json()`, query parameters
- API authentication: API keys, Bearer tokens, URL parameters
- Working with JSON responses and nested data structures
- `datetime` module for scheduling and time-based logic
- SMTP with `smtplib` for email notifications
- Environment variables for credential management (`os.environ`)
- HTML entity unescaping (`html.unescape()`)
- Python type hints and arrow annotations (`-> None`, `-> str`)
- `*args` and `**kwargs` for flexible function signatures
- List comprehension with conditionals: `[x for x in lst if condition]`
- Dictionary comprehension with conditionals
- Pixela API for habit graph creation via POST/PUT/DELETE
- BeautifulSoup (`bs4`) for HTML parsing and web scraping
- Projects: ISS Overhead Notifier, Rain Alert (OpenWeatherMap + Twilio), Habit Tracker, Workout Tracker, Amazon Price Tracker, Billboard Musical Time Machine, 100 Movies Scraper

### Day 48: Selenium Web Automation

- `webdriver` setup, browser launch, implicit and explicit waits
- Locating elements by ID, class, XPath, CSS selector
- Filling forms, clicking buttons, handling alerts
- Cookie-based session persistence
- Handling stale element references and click interception
- Project: Gym Booking Automation challenge

### Days 54–58: Flask Web Framework and Front-End Basics

- Flask application factory: `Flask(__name__)`, `app.run(debug=True)`
- Route definition with `@app.route()`, URL path variables (`<name>`, `<int:id>`)
- Python decorators: first-class functions, nested functions, wrapper pattern
- `render_template()` for serving HTML templates
- Jinja2 templating: `{{ variable }}`, `{% for %}`, `{% if %}` blocks, template inheritance (`{% extends %}`, `{% block %}`)
- Passing data from Python to templates (context variables)
- Calling external APIs inside Flask routes and rendering results in templates
- Static files: serving CSS and images via the `static/` directory
- HTML fundamentals: headings, paragraphs, void elements, lists, anchors, images
- CSS fundamentals: selectors, specificity, color, font properties, box model
- Bootstrap 5: grid system, utility classes, pre-built components (navbar, cards, buttons)
- `Bootstrap5()` integration with Flask
- Projects: Personal site, Jinja2 blog prototype, Bootstrap component exercises

### Days 63–65: Databases – SQLite and SQLAlchemy

- Raw SQLite via Python's built-in `sqlite3` module: `connect()`, `cursor()`, `execute()`, `commit()`
- Flask-SQLAlchemy ORM: `DeclarativeBase`, `db.Model`, `Mapped`, `mapped_column()`
- Column types: `Integer`, `String`, `Float`, `Boolean`, `Text`
- CRUD operations through the ORM session:
  - Create: `db.session.add()`, `db.session.commit()`
  - Read: `db.session.execute(db.select(Model))`, `.scalars().all()`, `.scalar()`
  - Read by primary key: `db.get_or_404(Model, id)`
  - Filter: `.where(Model.column == value)`
  - Update: modify attribute then `db.session.commit()`
  - Delete: `db.session.delete(obj)`, `db.session.commit()`
- `app.app_context()` requirement for database operations
- WTForms: `FlaskForm`, field types, validators (`DataRequired()`, `URL()`)
- `redirect()` and `url_for()` after POST (PRG pattern)
- Projects: Library app (full CRUD), SQLAlchemy standalone practice

### Day 66: RESTful API Design with Flask

- REST principles: resource-based URLs, HTTP verbs as actions
- Implementing GET, POST, PATCH, DELETE routes in Flask
- `jsonify()` for JSON responses with correct content-type
- `request.args.get()` for query string parameters
- `to_dict()` pattern using `self.__table__.columns` for automatic serialization
- API key authentication on sensitive endpoints
- HTTP status codes in responses: `200`, `403`, `404`
- Project: Cafe RESTful API (full CRUD)

### Day 67: Forms and Rich Text Editing

- `flask-ckeditor`: `CKEditor(app)`, `CKEditorField` in WTForms, WYSIWYG in templates
- Reusing a single form template for create and edit operations
- `date.today().strftime()` for auto-stamping records
- Project: Upgraded blog (full CRUD with WTForms + CKEditor + Bootstrap5)

### Day 68: Authentication and User Management

- `werkzeug.security`: `generate_password_hash()` (pbkdf2:sha256), `check_password_hash()`
- Never storing plain-text passwords; always hashing before persisting
- `flask-login`: `LoginManager`, `UserMixin`, `login_user()`, `logout_user()`, `current_user`, `@login_required`
- `@login_manager.user_loader` callback for session-based user retrieval
- Flash messages: `flash()` in routes, `get_flashed_messages()` in templates
- `send_from_directory()` for serving protected file downloads
- Duplicate registration detection before insert
- Project: Flask authentication system (register, login, logout, protected routes, file download)

---

## Tools and Libraries Reference

| Library / Tool        | Used In                                                     |
|-----------------------|-------------------------------------------------------------|
| `requests`            | API calls (ISS, weather, Spotify, TMDB, Kiwi)               |
| `pandas`              | DataFrame operations, CSV reading                           |
| `tkinter`             | GUI apps (password manager, quiz, flashcards, Pomodoro)     |
| `turtle`              | OOP games (Snake, Pong, TurtleCrossing)                     |
| `pygame`              | PCAP prep – GUI basics, event loop, font rendering          |
| `smtplib`             | Email notifications                                         |
| `sqlite3`             | Raw SQLite database access                                  |
| `flask`               | Web framework (routing, templates, forms)                   |
| `flask-sqlalchemy`    | ORM for SQLite/SQLAlchemy integration                       |
| `flask-wtf` / WTForms | Web forms with validation                                   |
| `flask-login`         | Session-based user authentication                           |
| `flask-ckeditor`      | Rich text editor in forms                                   |
| `flask-bootstrap`     | Bootstrap5 integration with Flask                           |
| `werkzeug.security`   | Password hashing and verification                           |
| `beautifulsoup4`      | HTML scraping and parsing                                   |
| `selenium`            | Browser automation                                          |
| `pathlib`             | Cross-platform file path management                         |
| `os.environ`          | Environment variable access for secrets                     |
| `json`                | Load/save JSON files for persistence                        |
| `datetime`            | Date/time operations                                        |
