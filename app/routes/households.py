from flask import Blueprint, render_template

households = Blueprint('households', __name__)

@households.route('/households')
def index():
    return render_template('households.html')
