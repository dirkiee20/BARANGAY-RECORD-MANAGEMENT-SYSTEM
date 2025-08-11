from flask import Blueprint, render_template

residents = Blueprint('residents', __name__)

@residents.route('/residents')
def index():
    return render_template('residents.html')
