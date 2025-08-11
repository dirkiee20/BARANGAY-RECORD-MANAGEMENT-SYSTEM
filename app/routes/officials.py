from flask import Blueprint, render_template

officials = Blueprint('officials', __name__)

@officials.route('/officials')
def index():
    return render_template('officials.html')
