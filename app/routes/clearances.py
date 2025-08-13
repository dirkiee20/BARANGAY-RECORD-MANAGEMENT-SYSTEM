from flask import Blueprint, render_template
from flask_login import login_required

clearances = Blueprint('clearances', __name__)

@clearances.route('/clearances')
@login_required
def index():
    return render_template('clearances.html')
