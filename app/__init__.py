from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


# Database extensions (imported by models via `from app import db`)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models so migrations can detect them
    from . import models

    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login user_loader callback."""
        return models.User.query.get(int(user_id))

    # Register HTTP routes
    from .routes import init_app as init_routes
    init_routes(app)

    # The db.create_all() call is removed.
    # It's better to manage the database schema with Flask-Migrate.
    # Use `flask db upgrade` to apply migrations.

    return app