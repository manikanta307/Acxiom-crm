# crm

A beginner-friendly CRM web application for a college project.

Project structure and responsibilities

- `app.py`: Flask application factory and app entrypoint.
- `config.py`: Configuration (secret key, database URI, other settings).
- `requirements.txt`: Python dependencies.
- `.gitignore`: Files to ignore in version control.
- `database/`: Contains the development SQLite database file `crm.db`.
- `models/`: SQLAlchemy models (database schema) will go here.
- `routes/`: Flask route blueprints and controllers.
- `services/`: Business logic and helpers (email, reports, audit log helpers).
- `templates/`: Jinja2 HTML templates (UI pages).
- `static/`: Static assets (CSS, JS, images). 

How to run (development):

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

2. Set environment variables (optional):

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
```

3. Run the app:

```bash
python app.py
```

Next steps:
- Implement models in `models/`.
- Implement routes and blueprints in `routes/`.
- Add templates and static assets.
- Implement authentication, authorization, and features per the assignment.

