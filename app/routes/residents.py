from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import Resident

residents = Blueprint('residents', __name__)

@residents.route('/residents')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    
    residents_query = Resident.query.order_by(Resident.last_name, Resident.first_name)
    if query:
        residents_query = residents_query.filter(Resident.first_name.ilike(f'%{query}%') | Resident.last_name.ilike(f'%{query}%'))
        
    pagination = residents_query.paginate(page=page, per_page=15, error_out=False)
    residents_list = pagination.items
    return render_template('residents.html', residents=residents_list, pagination=pagination, query=query)
