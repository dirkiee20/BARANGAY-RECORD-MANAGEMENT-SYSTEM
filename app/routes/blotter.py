from flask import Blueprint, render_template

blotter = Blueprint('blotter', __name__)

@blotter.route('/blotter')
def index():
    return render_template('blotter.html')
