from flask import Blueprint, render_template

clearances = Blueprint('clearances', __name__)

@clearances.route('/clearances')
def index():
    return render_template('clearances.html')
