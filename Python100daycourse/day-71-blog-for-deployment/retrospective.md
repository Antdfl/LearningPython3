# Flask Deployment Retrospective — Heliohost + PostgreSQL

## Overview

Checklist of issues encountered and how to resolve them when deploying a Flask app
with a vendor folder (no pip access) on a shared Apache/mod_wsgi host using PostgreSQL.

---

## Issue 1 — ModuleNotFoundError on import

**Symptom:** `ModuleNotFoundError: No module named 'flask_bootstrap'` (or any other library)

**Cause:** The `vendor/` folder was uploaded to the wrong directory (parent instead of app root).

**Fix:**
- Make sure `vendor/` sits at the same level as `main.py`
- The WSGI file must add it to `sys.path` with: `sys.path.insert(0, '/path/to/app/vendor')`

---

## Issue 2 — psycopg2 built for Windows, server runs Linux

**Symptom:** `AttributeError: module 'os' has no attribute 'add_dll_directory'`

**Cause:** `psycopg2-binary` was installed on Windows and vendor-bundled as-is.
The Windows wheel contains `delvewheel` patching code that calls `os.add_dll_directory`,
which does not exist on Linux.

**Fix:**
- Download the correct Linux wheel locally using pip with platform flags:
  ```
  pip download psycopg2-binary==<version> \
      --platform manylinux_2_17_x86_64 \
      --python-version <3XX> \
      --only-binary=:all: \
      -d ./tmp_download
  ```
- Extract the wheel (it is a zip file) and replace `vendor/psycopg2/`
  and `vendor/psycopg2_binary.libs/` with the Linux versions
- Check the server Python version first (e.g. Python 3.12 → `--python-version 312`)

---

## Issue 3 — Environment variables set via .htaccess not visible to the app

**Symptom:** App ignores `SetEnv` directives in `.htaccess` and falls back to SQLite

**Cause:** `SetEnv` in `.htaccess` sets Apache/CGI environment variables, which are
**not** propagated to `os.environ` in mod_wsgi daemon processes. They are only
available in the per-request WSGI environ dict, not at import time.

**Fix:**
- Set environment variables directly in the `.wsgi` file, **before** importing the app:
  ```python
  import os
  os.environ['POSTGRES_URI'] = 'postgresql://user:password@host:port/dbname'
  
  import sys
  sys.path.insert(0, '/path/to/vendor')
  sys.path.insert(0, '/path/to/app')
  from main import app as application
  ```

---

## Issue 4 — SQLite fallback: "unable to open database file"

**Symptom:** `sqlite3.OperationalError: unable to open database file`

**Cause:** No database URI environment variable was found, so the app fell back to
`sqlite:///./instance/posts.db`. The `instance/` directory does not exist on the server.

**Fix:**
- Ensure at least one of the expected env vars is set in the `.wsgi` file (see Issue 3)
- The fallback SQLite path is a development convenience only — never rely on it in production

---

## Issue 5 — PostgreSQL tables exist but with wrong schema (missing columns)

**Symptom:** `psycopg2.errors.UndefinedColumn: column users.email does not exist`

**Cause:** The `users` table was created by a previous run or manually, with a different
schema. SQLAlchemy's `db.create_all()` only creates tables that do not exist — it never
modifies existing ones.

**Fix:**
- Drop and recreate the tables using a dedicated reset script (see `main2.py`)
- Script must: connect to the correct DB, call `db.drop_all()`, then `db.create_all()`
- Verify by inspecting the column list after creation before restoring the main app

---

## Issue 6 — Two database users, app connecting to the wrong one

**Symptom:** Reset script works fine and confirms correct columns, but the main app
still fails with the same missing-column error after restore.

**Cause:** The app's `get_database_uri()` checked env vars in an order that picked up
a secondary variable (e.g. `SQLALCHEMY_DATABASE_URI`) pointing to a different
database user/schema, which had a stale `users` table without the expected columns.

**Fix:**
- Always prioritize the explicitly set variable (`POSTGRES_URI`) over generic ones:
  ```python
  env_keys = ['POSTGRES_URI', 'DB_URI', 'DATABASE_URL', 'SQLALCHEMY_DATABASE_URI']
  ```
- Use only one database user for the application; remove or ignore extras
- Add logging so the app reports which URI it is actually using at startup

---

## Issue 7 — mod_wsgi worker not reloading after file changes

**Symptom:** New code uploaded and `flask.wsgi` touched, but old behavior persists.
Apache error log shows the same worker PID handling requests for 30+ minutes.

**Cause:** mod_wsgi daemon workers can keep running indefinitely if they keep receiving
requests. Touching the `.wsgi` file signals a reload, but an active worker may not
be killed immediately. On shared hosting, Apache cannot be restarted manually.

**Fix:**
- On many host, the wsgi server restarts automatically every ~2 hours — wait for it
- If a control panel "Restart Apache" button is available, use it
- To verify the worker reloaded, check that the PID in the error log has changed

---

## General Checklist for Future Deployments

- [ ] `vendor/` is in the same directory as `main.py`
- [ ] `vendor/psycopg2` is the Linux build matching the server Python version
- [ ] Database URI is set via `os.environ` in the `.wsgi` file, not `.htaccess`
- [ ] `get_database_uri()` checks the explicitly set variable first
- [ ] `SQLALCHEMY_ENGINE_OPTIONS` sets `search_path=public` to avoid schema conflicts
- [ ] Tables are created fresh on first deploy (no stale schema from a previous setup)
- [ ] After uploading new code, verify the worker PID changed in the error log
