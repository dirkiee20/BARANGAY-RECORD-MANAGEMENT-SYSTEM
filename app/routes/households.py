from flask import Blueprint, render_template, request
from flask_login import login_required
from datetime import date
from app.models import Household, Resident
from app import db

households = Blueprint('households', __name__)

@households.route('/households')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')

    # Base query
    households_query = Household.query.order_by(Household.id.desc())

    # Search functionality
    if query:
        search_term = f'%{query}%'
        # Join with residents to search by head of family name
        households_query = households_query.join(Household.head, isouter=True).filter(
            db.or_(
                (Resident.first_name + ' ' + Resident.last_name).ilike(search_term),
                Household.address.ilike(search_term),
                Household.purok.ilike(search_term)
            )
        )

    # Pagination
    pagination = households_query.paginate(page=page, per_page=10, error_out=False)
    households_list = pagination.items

    # Stats
    total_households = Household.query.count()
    total_residents = Resident.query.count()
    avg_members = (total_residents / total_households) if total_households > 0 else 0

    stats = {
        'total_households': total_households,
        'avg_members': f'{avg_members:.1f}',
    }

    return render_template('households.html', households=households_list, pagination=pagination, query=query, stats=stats)

@households.route('/household/<int:household_id>')
@login_required
def view(household_id):
    """Displays the details of a single household."""
    household = Household.query.get_or_404(household_id)
    # We pass today's date to calculate age in the template
    return render_template('view_household.html', household=household, today=date.today())
