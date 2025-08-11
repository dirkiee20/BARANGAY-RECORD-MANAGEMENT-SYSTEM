from flask import Blueprint
from .auth import auth
from .dashboard import dashboard
from .residents import residents
from .households import households
from .blotter import blotter
from .clearances import clearances
from .officials import officials
from .reports import reports

def init_app(app):
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(residents)
    app.register_blueprint(households)
    app.register_blueprint(blotter)
    app.register_blueprint(clearances)
    app.register_blueprint(officials)
    app.register_blueprint(reports)
