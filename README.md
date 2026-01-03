# Hassle-Free Parking System

A Django-based web application to search, book, and manage parking slots. It includes user authentication, booking lifecycle (reserve, start, end), feedback, and admin exports.

## Project structure

- `core/` – project config (settings, urls, WSGI/ASGI)
- `parking/` – main app (models, views, forms, urls, admin, signals, management commands)
- `templates/` – site templates (including `templates/parking/*`)
- `static/` – static assets (`css`, `js`, `images`)
- `db.sqlite3` – default SQLite database
- `manage.py` – Django management entry point

## Prerequisites

- Python 3.10+ (3.11 recommended)
- pip (Python package manager)

## Quick start (Windows PowerShell)

```powershell
# 1) Go to the project folder
cd "c:\Users\thati\OneDrive\Pictures\Desktop\File\Hassle-Free-Parking-System"

# 2) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Install dependencies
pip install -r requirements.txt

# 4) Apply database migrations
python manage.py migrate

# 5) Create a superuser (optional, for admin site)
python manage.py createsuperuser

# 6) Run the development server
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Configuration notes

- Database: uses SQLite by default (`db.sqlite3`). To change, edit `core/settings.py`.
- Static files: served from `static/` during development. For production, configure `STATIC_ROOT` and run `python manage.py collectstatic`.
- Templates: the main templates live under `templates/parking/`.

## Management commands

There is a custom command to expire reserved bookings that were never started:

```powershell
python manage.py expire_reserved_bookings
```

You can schedule it (e.g., Windows Task Scheduler) to run periodically.

## Running tests

A starter test file exists at `parking/tests.py`. Add unit tests using Django's test framework and run:

```powershell
python manage.py test
```

## Troubleshooting

- If you see "Couldn't import Django", ensure your virtual environment is activated and dependencies are installed.
- If migrations fail, check for pending model changes or delete `db.sqlite3` (development only) and re-run `migrate`.
- For static files not loading, verify `DEBUG=True` in `core/settings.py` during development or configure static serving for production.

## Next steps

- Add more tests (models, forms, views).
- Document API endpoints and view routes in `README.md`.
- Consider environment variables for secrets and production settings.
