from flask import Flask
from config import Config
from pathlib import Path
from flask import current_app
from extensions import db, login_manager, csrf


# module-level user_loader registered early to ensure availability during reloader cycles
@login_manager.user_loader
def _load_user_modulelevel(user_id):
    try:
        from models.user import User
        return User.query.get(int(user_id))
    except Exception:
        return None


# provide a no-op request loader so Flask-Login doesn't raise when no session user exists
@login_manager.request_loader
def _request_loader_noop(request):
    return None


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    # Respect explicit debug flag from config/env
    app.debug = app.config.get('DEBUG', False)

    # register user loader before initializing the extension to ensure it's available
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from models.user import User
            return User.query.get(int(user_id))
        except Exception:
            return None

    db.init_app(app)
    login_manager.init_app(app)
    # ensure the app-bound login_manager has the user loader set (defensive)
    try:
        login_manager._user_callback = load_user
        app.login_manager._user_callback = load_user
    except Exception:
        pass
    # debug info
    if app.debug:
        try:
            print('DEBUG: login_manager id', id(login_manager))
            print('DEBUG: app.login_manager id', id(app.login_manager))
            print('DEBUG: has user callback?', getattr(login_manager, '_user_callback', None) is not None)
            print('DEBUG: app.login_manager has user callback?', getattr(app.login_manager, '_user_callback', None) is not None)
            print('DEBUG: app.extensions login_manager', app.extensions.get('login_manager'))
            lm_ext = app.extensions.get('login_manager')
            if lm_ext is not None:
                print('DEBUG: ext id', id(lm_ext), 'has callback?', getattr(lm_ext, '_user_callback', None) is not None)
        except Exception:
            pass
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    # Ensure database folder exists and database file is present (empty file created if needed)
    db_path = Path(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        # create an empty file; actual tables will be created by models/migrations
        db_path.touch()

    # Blueprints will be registered here (routes/)

    # register blueprints
    from routes import register_blueprints
    register_blueprints(app)

    # Ensure CSRF is enabled for all routes (we render CSRF token inputs in templates)
    # Remove any temporary exemptions used during earlier debugging.

    # import models so that they are registered with SQLAlchemy
    import models  # noqa: F401

    # create tables if they don't exist (simple dev setup)
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            # If tables already exist or there is a benign race during reload,
            # ignore and continue — existing data should be preserved.
            pass

    @app.before_request
    def _ensure_user_loader():
        try:
            lm = current_app.login_manager
            if getattr(lm, '_user_callback', None) is None:
                from models.user import User

                def _loader(uid):
                    try:
                        return User.query.get(int(uid))
                    except Exception:
                        return None

                lm._user_callback = _loader
        except Exception:
            pass

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
