from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Database extensions (imported by models via `from app import db`)
db = SQLAlchemy()
migrate = Migrate()


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


    # Import models so migrations can detect them
    from . import models  # noqa: F401

    # Register HTTP routes
    from . import routes  # Import routes to register them with the app
    app.register_blueprint(routes.bp)

    # Optionally create tables for first run (ok with SQLite)
    with app.app_context():
        db.create_all()

    return app