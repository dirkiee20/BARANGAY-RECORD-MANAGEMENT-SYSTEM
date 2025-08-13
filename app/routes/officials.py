from flask import Blueprint, render_template
from flask_login import login_required

officials = Blueprint('officials', __name__)

@officials.route('/officials')
@login_required
def index():
    return render_template('officials.html')
