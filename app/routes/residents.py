from flask import Blueprint, render_template
from flask_login import login_required

residents = Blueprint('residents', __name__)

@residents.route('/residents')
@login_required
def index():
    return render_template('residents.html')
