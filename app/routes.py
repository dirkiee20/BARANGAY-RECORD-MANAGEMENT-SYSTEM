from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('login.html')


@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@bp.route('/residents')
def residents():
    return render_template('residents.html')


@bp.route('/households')
def households():
    return render_template('households.html')


@bp.route('/blotter')
def blotter():
    return render_template('blotter.html')


@bp.route('/clearances')
def clearances():
    return render_template('clearances.html')


@bp.route('/officials')
def officials():
    return render_template('officials.html')


@bp.route('/reports')
def reports():
    return render_template('reports.html')