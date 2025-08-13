from flask import Blueprint, render_template
from flask_login import login_required

reports = Blueprint('reports', __name__)

@reports.route('/reports')
@login_required
def index():
    return render_template('reports.html')
