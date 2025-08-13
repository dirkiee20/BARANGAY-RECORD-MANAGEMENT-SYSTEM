from flask import Blueprint, render_template
from flask_login import login_required

households = Blueprint('households', __name__)

@households.route('/households')
@login_required
def index():
    return render_template('households.html')
