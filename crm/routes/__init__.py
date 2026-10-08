from flask import Blueprint

def register_blueprints(app):
    from .auth import auth_bp
    from .main import main_bp
    from .customers import customers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(customers_bp)
