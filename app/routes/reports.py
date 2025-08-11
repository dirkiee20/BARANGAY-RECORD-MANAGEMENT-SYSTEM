from flask import Blueprint, render_template

reports = Blueprint('reports', __name__)

@reports.route('/reports')
def index():
    return render_template('reports.html')
