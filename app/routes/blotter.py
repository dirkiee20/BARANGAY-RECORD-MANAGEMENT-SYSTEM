from flask import Blueprint, render_template
from flask_login import login_required

blotter = Blueprint('blotter', __name__)

@blotter.route('/blotter')
@login_required
def index():
    return render_template('blotter.html')
