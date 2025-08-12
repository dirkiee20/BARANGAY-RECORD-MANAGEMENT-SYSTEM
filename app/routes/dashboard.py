from flask import Blueprint, render_template, jsonify, request, current_app
from app import db
from app.models import Resident, Household, Blotter, Clearance, Official
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy import text
import json
import os
from werkzeug.utils import secure_filename

dashboard = Blueprint('dashboard', __name__)

def get_monthly_stats():
    """Get statistics for the current month"""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_stats = {
        'residents_added': Resident.query.filter(
            Resident.created_at >= month_start
        ).count(),
        'households_added': Household.query.filter(
            Household.created_at >= month_start
        ).count(),
        'clearances_issued': Clearance.query.filter(
            Clearance.status == 'Issued',
            Clearance.issued_at >= month_start
        ).count(),
        'blotters_resolved': Blotter.query.filter(
            Blotter.status == 'Resolved',
            Blotter.reported_at >= month_start
        ).count()
    }
    
    return monthly_stats

@dashboard.route('/dashboard')
def index():
    try:
        # Get current date and calculate date ranges
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Query statistics
        total_residents = Resident.query.count()
        total_households = Household.query.count()
        
        # Residents added this week
        new_residents_week = Resident.query.filter(
            Resident.created_at >= week_ago
        ).count()
        
        # Households added this week
        new_households_week = Household.query.filter(
            Household.created_at >= week_ago
        ).count()
        
        # Active blotters (Open status)
        active_blotters = Blotter.query.filter(
            Blotter.status == 'Open'
        ).count()
        
        # Blotters due today (hearing date is today)
        today = now.date()
        blotters_due_today = Blotter.query.filter(
            func.date(Blotter.hearing_date) == today
        ).count()
        
        # Clearances issued in last 30 days
        clearances_issued_month = Clearance.query.filter(
            Clearance.status == 'Issued',
            Clearance.issued_at >= month_ago
        ).count()
        
        # Recent residents (last 5 added)
        recent_residents = Resident.query.order_by(
            Resident.created_at.desc()
        ).limit(5).all()
        
        # Open blotters (last 5)
        open_blotters = Blotter.query.filter(
            Blotter.status == 'Open'
        ).order_by(Blotter.reported_at.desc()).limit(5).all()
        
        # Pending clearances
        pending_clearances = Clearance.query.filter(
            Clearance.status == 'Pending'
        ).count()
        
        # Processed clearances today
        clearances_processed_today = Clearance.query.filter(
            Clearance.status == 'Issued',
            func.date(Clearance.issued_at) == today
        ).count()
        
        # Get monthly statistics
        monthly_stats = get_monthly_stats()
        
        # Calculate age for residents
        for resident in recent_residents:
            if resident.birth_date:
                age = (now.date() - resident.birth_date).days // 365
                resident.age = age
            else:
                resident.age = 'N/A'
        
        # Prepare dashboard data
        dashboard_data = {
            'stats': {
                'total_residents': total_residents,
                'total_households': total_households,
                'new_residents_week': new_residents_week,
                'new_households_week': new_households_week,
                'active_blotters': active_blotters,
                'blotters_due_today': blotters_due_today,
                'clearances_issued_month': clearances_issued_month
            },
            'monthly_stats': monthly_stats,
            'recent_residents': recent_residents,
            'open_blotters': open_blotters,
            'clearance_summary': {
                'pending': pending_clearances,
                'processed_today': clearances_processed_today
            },
            'today': today
        }
        
        return render_template('dashboard.html', data=dashboard_data)
        
    except Exception as e:
        # Log the error (in production, you'd want proper logging)
        print(f"Dashboard error: {e}")
        
        # Return dashboard with empty data
        dashboard_data = {
            'stats': {
                'total_residents': 0,
                'total_households': 0,
                'new_residents_week': 0,
                'new_households_week': 0,
                'active_blotters': 0,
                'blotters_due_today': 0,
                'clearances_issued_month': 0
            },
            'monthly_stats': {
                'residents_added': 0,
                'households_added': 0,
                'clearances_issued': 0,
                'blotters_resolved': 0
            },
            'recent_residents': [],
            'open_blotters': [],
            'clearance_summary': {
                'pending': 0,
                'processed_today': 0
            },
            'today': datetime.utcnow().date()
        }
        
        return render_template('dashboard.html', data=dashboard_data)

@dashboard.route('/api/dashboard-stats')
def api_dashboard_stats():
    """API endpoint to get dashboard statistics"""
    try:
        # Test database connection first
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as db_error:
            print(f"Database connection error: {db_error}")
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get current date and calculate date ranges
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Query statistics with individual error handling
        try:
            total_residents = Resident.query.count()
            print(f"Total residents: {total_residents}")
        except Exception as e:
            print(f"Error counting residents: {e}")
            total_residents = 0
            
        try:
            total_households = Household.query.count()
            print(f"Total households: {total_households}")
        except Exception as e:
            print(f"Error counting households: {e}")
            total_households = 0
        
        # Residents added this week
        try:
            new_residents_week = Resident.query.filter(
                Resident.created_at >= week_ago
            ).count()
        except Exception as e:
            print(f"Error counting new residents: {e}")
            new_residents_week = 0
        
        # Households added this week
        try:
            new_households_week = Household.query.filter(
                Household.created_at >= week_ago
            ).count()
        except Exception as e:
            print(f"Error counting new households: {e}")
            new_households_week = 0
        
        # Active blotters (Open status)
        try:
            active_blotters = Blotter.query.filter(
                Blotter.status == 'Open'
            ).count()
        except Exception as e:
            print(f"Error counting active blotters: {e}")
            active_blotters = 0
        
        # Blotters due today (hearing date is today)
        today = now.date()
        try:
            blotters_due_today = Blotter.query.filter(
                func.date(Blotter.hearing_date) == today
            ).count()
        except Exception as e:
            print(f"Error counting blotters due today: {e}")
            blotters_due_today = 0
        
        # Clearances issued in last 30 days
        try:
            clearances_issued_month = Clearance.query.filter(
                Clearance.status == 'Issued',
                Clearance.issued_at >= month_ago
            ).count()
        except Exception as e:
            print(f"Error counting clearances: {e}")
            clearances_issued_month = 0
        
        # Recent residents (last 5 added)
        try:
            recent_residents = Resident.query.order_by(
                Resident.created_at.desc()
            ).limit(5).all()
        except Exception as e:
            print(f"Error fetching recent residents: {e}")
            recent_residents = []
        
        # Open blotters (last 5)
        try:
            open_blotters = Blotter.query.filter(
                Blotter.status == 'Open'
            ).order_by(Blotter.reported_at.desc()).limit(5).all()
        except Exception as e:
            print(f"Error fetching open blotters: {e}")
            open_blotters = []
        
        # Pending clearances
        try:
            pending_clearances = Clearance.query.filter(
                Clearance.status == 'Pending'
            ).count()
        except Exception as e:
            print(f"Error counting pending clearances: {e}")
            pending_clearances = 0
        
        # Processed clearances today
        try:
            clearances_processed_today = Clearance.query.filter(
                Clearance.status == 'Issued',
                func.date(Clearance.issued_at) == today
            ).count()
        except Exception as e:
            print(f"Error counting processed clearances: {e}")
            clearances_processed_today = 0
        
        # Calculate age for residents
        for resident in recent_residents:
            if resident.birth_date:
                age = (now.date() - resident.birth_date).days // 365
                resident.age = age
            else:
                resident.age = 'N/A'
        
        # Prepare dashboard data
        dashboard_data = {
            'stats': {
                'total_residents': total_residents,
                'total_households': total_households,
                'new_residents_week': new_residents_week,
                'new_households_week': new_households_week,
                'active_blotters': active_blotters,
                'blotters_due_today': blotters_due_today,
                'clearances_issued_month': clearances_issued_month
            },
            'recent_residents': [
                {
                    'id': r.id,
                    'first_name': r.first_name,
                    'last_name': r.last_name,
                    'address': r.address,
                    'age': r.age,
                    'status': r.status
                } for r in recent_residents
            ],
            'open_blotters': [
                {
                    'id': b.id,
                    'case_title': b.case_title,
                    'location': b.location,
                    'hearing_date': b.hearing_date.isoformat() if b.hearing_date else None,
                    'reported_by': {
                        'first_name': b.reported_by.first_name,
                        'last_name': b.reported_by.last_name
                    } if b.reported_by else None
                } for b in open_blotters
            ],
            'clearance_summary': {
                'pending': pending_clearances,
                'processed_today': clearances_processed_today
            }
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        print(f"API Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500

@dashboard.route('/api/record-types')
def api_record_types():
    """API endpoint to get available record types"""
    record_types = [
        {'value': 'resident', 'label': 'New Resident'},
        {'value': 'household', 'label': 'New Household'},
        {'value': 'blotter', 'label': 'New Blotter Case'},
        {'value': 'clearance', 'label': 'New Clearance Request'}
    ]
    return jsonify(record_types)

@dashboard.route('/api/new-record', methods=['POST'])
def api_new_record():
    """API endpoint to create a new record"""
    try:
        record_type = request.form.get('recordType')
        
        if not record_type:
            return jsonify({'error': 'Record type is required'}), 400
        
        if record_type == 'resident':
            return create_new_resident(request.form)
        elif record_type == 'household':
            return create_new_household(request.form)
        elif record_type == 'blotter':
            return create_new_blotter(request.form)
        elif record_type == 'clearance':
            return create_new_clearance(request.form)
        else:
            return jsonify({'error': 'Invalid record type'}), 400
            
    except Exception as e:
        print(f"New record error: {e}")
        return jsonify({'error': 'Failed to create record'}), 500

def create_new_resident(form_data):
    """Create a new resident record"""
    try:
        # Extract form data
        first_name = form_data.get('firstName', '').strip()
        middle_name = form_data.get('middleName', '').strip()
        last_name = form_data.get('lastName', '').strip()
        alias = form_data.get('alias', '').strip()
        place_of_birth = form_data.get('placeOfBirth', '').strip()
        birth_date_str = form_data.get('birthDate', '')
        civil_status = form_data.get('civilStatus', '').strip()
        purok = form_data.get('purok', '').strip()
        voters_status = form_data.get('votersStatus', '').strip()
        identified_as = form_data.get('identifiedAs', '').strip()
        email = form_data.get('email', '').strip()
        occupation = form_data.get('occupation', '').strip()
        citizenship = form_data.get('citizenship', '').strip()
        sex = form_data.get('sex', '')
        address = form_data.get('address', '').strip()
        contact_number = form_data.get('contactNumber', '').strip()
        
        # Validation
        if not first_name or not last_name or not address:
            return jsonify({'error': 'First name, last name, and address are required'}), 400
        
        # Parse birth date
        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid birth date format'}), 400
        
        # Handle file upload
        profile_picture = request.files.get('profilePicture')
        profile_picture_path = None
        if profile_picture:
            # You would typically save the file to a secure location
            # and store the path in the database. For this example,
            # we'll just store the filename.
            filename = secure_filename(profile_picture.filename)
            # Ensure the 'uploads' directory exists
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            profile_picture_path = os.path.join(upload_folder, filename)
            profile_picture.save(profile_picture_path)
            profile_picture_path = os.path.join('uploads', filename)


        # Create resident
        resident = Resident(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            alias=alias,
            place_of_birth=place_of_birth,
            birth_date=birth_date,
            civil_status=civil_status,
            purok=purok,
            voters_status=voters_status,
            identified_as=identified_as,
            email=email,
            occupation=occupation,
            citizenship=citizenship,
            profile_picture=profile_picture_path,
            sex=sex,
            address=address,
            contact_number=contact_number,
            status='Active'
        )
        
        db.session.add(resident)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Resident created successfully',
            'resident_id': resident.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Create resident error: {e}")
        return jsonify({'error': 'Failed to create resident'}), 500

def create_new_household(form_data):
    """Create a new household record"""
    try:
        # Extract form data
        head_name = form_data.get('headName', '').strip()
        address = form_data.get('address', '').strip()
        purok = form_data.get('purok', '').strip()
        contact_number = form_data.get('contactNumber', '').strip()
        
        # Validation
        if not head_name or not address:
            return jsonify({'error': 'Head name and address are required'}), 400
        
        # Create household
        household = Household(
            head_name=head_name,
            address=address,
            purok=purok if purok else None,
            contact_number=contact_number if contact_number else None
        )
        
        db.session.add(household)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Household created successfully',
            'household_id': household.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Create household error: {e}")
        return jsonify({'error': 'Failed to create household'}), 500

def create_new_blotter(form_data):
    """Create a new blotter record"""
    try:
        # Extract form data
        case_title = form_data.get('caseTitle', '').strip()
        case_type = form_data.get('caseType', '').strip()
        details = form_data.get('details', '').strip()
        location = form_data.get('location', '').strip()
        respondent_name = form_data.get('respondentName', '').strip()
        
        # Validation
        if not case_title or not details:
            return jsonify({'error': 'Case title and details are required'}), 400
        
        # Create blotter
        blotter = Blotter(
            case_title=case_title,
            case_type=case_type if case_type else None,
            details=details,
            location=location if location else None,
            status='Open'
        )
        
        db.session.add(blotter)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Blotter case created successfully',
            'blotter_id': blotter.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Create blotter error: {e}")
        return jsonify({'error': 'Failed to create blotter case'}), 500

def create_new_clearance(form_data):
    """Create a new clearance record"""
    try:
        # Extract form data
        clearance_type = form_data.get('clearanceType', '').strip()
        purpose = form_data.get('purpose', '').strip()
        resident_id = form_data.get('residentId', '').strip()
        
        # Validation
        if not clearance_type or not purpose:
            return jsonify({'error': 'Clearance type and purpose are required'}), 400
        
        # Check if resident exists
        if resident_id:
            resident = Resident.query.get(resident_id)
            if not resident:
                return jsonify({'error': 'Selected resident not found'}), 400
        
        # Create clearance
        clearance = Clearance(
            clearance_type=clearance_type,
            purpose=purpose,
            resident_id=int(resident_id) if resident_id else None,
            status='Pending'
        )
        
        db.session.add(clearance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Clearance request created successfully',
            'clearance_id': clearance.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Create clearance error: {e}")
        return jsonify({'error': 'Failed to create clearance request'}), 500

@dashboard.route('/api/search')
def api_search():
    """API endpoint for searching records"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'results': []})
        
        # Search residents
        residents = Resident.query.filter(
            db.or_(
                Resident.first_name.ilike(f'%{query}%'),
                Resident.last_name.ilike(f'%{query}%'),
                Resident.address.ilike(f'%{query}%')
            )
        ).limit(5).all()
        
        # Search blotters
        blotters = Blotter.query.filter(
            Blotter.case_title.ilike(f'%{query}%')
        ).limit(5).all()
        
        results = {
            'residents': [
                {
                    'id': r.id,
                    'name': f"{r.first_name} {r.last_name}",
                    'address': r.address,
                    'type': 'resident'
                } for r in residents
            ],
            'blotters': [
                {
                    'id': b.id,
                    'title': b.case_title,
                    'status': b.status,
                    'type': 'blotter'
                } for b in blotters
            ]
        }
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@dashboard.route('/api/residents')
def api_residents():
    """API endpoint to get all residents for dropdown selection"""
    try:
        residents = Resident.query.filter(
            Resident.status == 'Active'
        ).order_by(Resident.last_name, Resident.first_name).all()
        
        residents_data = [
            {
                'id': r.id,
                'first_name': r.first_name,
                'last_name': r.last_name,
                'address': r.address
            } for r in residents
        ]
        
        return jsonify(residents_data)
        
    except Exception as e:
        print(f"Residents API error: {e}")
        return jsonify({'error': 'Failed to fetch residents'}), 500

@dashboard.route('/dashboard/test-data')
def insert_test_data():
    """Insert sample data for testing dashboard functionality"""
    try:
        from datetime import date
        
        # Check if data already exists
        if Resident.query.count() > 0:
            return "Test data already exists!"
        
        # Create sample households
        household1 = Household(
            head_name="Juan Dela Cruz",
            address="123 Main Street, Purok 1",
            purok="Purok 1"
        )
        household2 = Household(
            head_name="Maria Santos",
            address="456 Oak Avenue, Purok 2", 
            purok="Purok 2"
        )
        
        db.session.add(household1)
        db.session.add(household2)
        db.session.commit()
        
        # Create sample residents
        resident1 = Resident(
            first_name="Juan",
            last_name="Dela Cruz",
            sex="Male",
            birth_date=date(1985, 5, 15),
            address="123 Main Street, Purok 1",
            status="Active",
            household_id=household1.id
        )
        resident2 = Resident(
            first_name="Maria",
            last_name="Santos",
            sex="Female", 
            birth_date=date(1990, 8, 22),
            address="456 Oak Avenue, Purok 2",
            status="Active",
            household_id=household2.id
        )
        resident3 = Resident(
            first_name="Ana",
            last_name="Lopez",
            sex="Female",
            birth_date=date(1995, 3, 10),
            address="789 Pine Road, Purok 3",
            status="Active"
        )
        
        db.session.add(resident1)
        db.session.add(resident2)
        db.session.add(resident3)
        db.session.commit()
        
        # Create sample blotters
        blotter1 = Blotter(
            case_title="Noise Complaint",
            details="Loud music playing late at night",
            status="Open",
            location="Purok 1",
            reported_by_id=resident1.id
        )
        blotter2 = Blotter(
            case_title="Boundary Dispute",
            details="Property line disagreement between neighbors",
            status="Open", 
            location="Purok 2",
            reported_by_id=resident2.id
        )
        
        db.session.add(blotter1)
        db.session.add(blotter2)
        db.session.commit()
        
        # Create sample clearances
        clearance1 = Clearance(
            clearance_type="Barangay Clearance",
            purpose="Employment",
            status="Issued",
            issued_at=datetime.utcnow(),
            resident_id=resident1.id
        )
        clearance2 = Clearance(
            clearance_type="Indigency Certificate",
            purpose="Government Assistance",
            status="Pending",
            resident_id=resident2.id
        )
        
        db.session.add(clearance1)
        db.session.add(clearance2)
        db.session.commit()
        
        return "Test data inserted successfully! Dashboard should now show real data."
        
    except Exception as e:
        db.session.rollback()
        return f"Error inserting test data: {str(e)}"

@dashboard.route('/api/insert-sample-data')
def insert_sample_data():
    """Insert sample data for testing"""
    try:
        from app import db
        
        # Check if data already exists
        if Resident.query.count() > 0:
            return jsonify({
                'status': 'info',
                'message': 'Sample data already exists'
            })
        
        print("Starting sample data creation...")
        
        # Create sample household
        household = Household(
            head_name='Juan Dela Cruz',
            address='123 Main Street, Barangay San Jose',
            purok='Purok 1',
            contact_number='09123456789'
        )
        db.session.add(household)
        db.session.commit()  # Commit household first
        print(f"Created household with ID: {household.id}")
        
        # Create sample resident
        resident = Resident(
            first_name='Juan',
            last_name='Dela Cruz',
            sex='Male',
            address='123 Main Street, Barangay San Jose',
            contact_number='09123456789',
            email='juan@example.com',
            status='Active'
        )
        db.session.add(resident)
        db.session.commit()  # Commit resident to get ID
        
        # Verify resident ID was generated
        if not resident.id:
            raise Exception("Resident ID was not generated")
        
        print(f"Created resident with ID: {resident.id}")
        
        # Double-check resident exists in database
        resident_check = Resident.query.get(resident.id)
        if not resident_check:
            raise Exception(f"Resident with ID {resident.id} not found in database after commit")
        print(f"Verified resident exists in database: {resident_check.first_name} {resident_check.last_name}")
        
        # Also check with a direct SQL query to be sure
        try:
            result = db.session.execute('SELECT id, first_name, last_name FROM residents WHERE id = :id', {'id': resident.id})
            row = result.fetchone()
            if not row:
                raise Exception(f"Resident not found in direct SQL query")
            print(f"Direct SQL query confirmed resident: {row[1]} {row[2]}")
        except Exception as sql_error:
            print(f"SQL query error: {sql_error}")
            raise Exception(f"Failed to verify resident with SQL: {sql_error}")
        
        # Create sample blotter
        blotter = Blotter(
            case_title='Noise Complaint',
            case_type='Complaint',
            details='Loud music playing late at night',
            status='Open',
            location='123 Main Street'
        )
        db.session.add(blotter)
        db.session.commit()  # Commit blotter
        print(f"Created blotter with ID: {blotter.id}")
        
        # Create sample clearance - now with proper resident ID
        clearance = Clearance(
            clearance_type='Barangay Clearance',
            purpose='Employment',
            status='Pending',
            resident_id=resident.id  # Use the actual resident ID
        )
        print(f"Creating clearance with resident_id: {resident.id}")
        db.session.add(clearance)
        db.session.commit()  # Commit clearance
        print(f"Created clearance with ID: {clearance.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Sample data inserted successfully',
            'counts': {
                'households': Household.query.count(),
                'residents': Resident.query.count(),
                'blotters': Blotter.query.count(),
                'clearances': Clearance.query.count()
            },
            'resident_id_used': resident.id
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error in sample data creation: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to insert sample data: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@dashboard.route('/api/test-db')
def test_database():
    """Simple endpoint to test database connectivity"""
    try:
        # Test basic connection
        db.session.execute('SELECT 1')
        
        # Test if tables exist
        tables = []
        try:
            residents_count = Resident.query.count()
            tables.append(f"Residents: {residents_count}")
        except Exception as e:
            tables.append(f"Residents table error: {str(e)}")
            
        try:
            households_count = Household.query.count()
            tables.append(f"Households: {households_count}")
        except Exception as e:
            tables.append(f"Households table error: {str(e)}")
            
        try:
            blotters_count = Blotter.query.count()
            tables.append(f"Blotters: {blotters_count}")
        except Exception as e:
            tables.append(f"Blotters table error: {str(e)}")
            
        try:
            clearances_count = Clearance.query.count()
            tables.append(f"Clearances: {clearances_count}")
        except Exception as e:
            tables.append(f"Clearances table error: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'tables': tables
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@dashboard.route('/api/create-tables')
def create_database_tables():
    """Create database tables if they don't exist"""
    try:
        from app import db
        
        # Create all tables
        db.create_all()
        
        return jsonify({
            'status': 'success',
            'message': 'Database tables created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to create tables: {str(e)}'
        }), 500

@dashboard.route('/api/db-info')
def database_info():
    """Get database connection information"""
    try:
        from app import db
        from config import Config
        
        # Get database URI (masked for security)
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        if 'postgresql://' in db_uri:
            # Mask password in URI
            parts = db_uri.split('@')
            if len(parts) == 2:
                user_pass = parts[0].replace('postgresql://', '')
                if ':' in user_pass:
                    user, password = user_pass.split(':', 1)
                    masked_uri = f"postgresql://{user}:***@{parts[1]}"
                else:
                    masked_uri = f"postgresql://{user_pass}@{parts[1]}"
            else:
                masked_uri = "postgresql://***"
        else:
            masked_uri = db_uri
            
        return jsonify({
            'status': 'success',
            'database_uri': masked_uri,
            'database_type': 'PostgreSQL' if 'postgresql://' in db_uri else 'Other',
            'sqlalchemy_track_modifications': Config.SQLALCHEMY_TRACK_MODIFICATIONS
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get database info: {str(e)}'
        }), 500

@dashboard.route('/api/fix-database-schema')
def fix_database_schema():
    """Add missing columns to existing database tables"""
    try:
        from app import db
        
        # Check what columns exist and add missing ones
        changes_made = []
        
        # Check residents table
        try:
            # Try to add contact_number column
            db.session.execute('ALTER TABLE residents ADD COLUMN IF NOT EXISTS contact_number VARCHAR(20)')
            changes_made.append("Added contact_number to residents table")
        except Exception as e:
            changes_made.append(f"contact_number column: {str(e)}")
            
        try:
            # Try to add email column
            db.session.execute('ALTER TABLE residents ADD COLUMN IF NOT EXISTS email VARCHAR(120)')
            changes_made.append("Added email to residents table")
        except Exception as e:
            changes_made.append(f"email column: {str(e)}")
        
        # Check households table
        try:
            # Try to add contact_number column
            db.session.execute('ALTER TABLE households ADD COLUMN IF NOT EXISTS contact_number VARCHAR(20)')
            changes_made.append("Added contact_number to households table")
        except Exception as e:
            changes_made.append(f"households contact_number column: {str(e)}")
        
        # Check blotters table
        try:
            # Try to add case_type column
            db.session.execute('ALTER TABLE blotters ADD COLUMN IF NOT EXISTS case_type VARCHAR(50)')
            changes_made.append("Added case_type to blotters table")
        except Exception as e:
            changes_made.append(f"case_type column: {str(e)}")
            
        try:
            # Try to add respondent_name column
            db.session.execute('ALTER TABLE blotters ADD COLUMN IF NOT EXISTS respondent_name VARCHAR(120)')
            changes_made.append("Added respondent_name to blotters table")
        except Exception as e:
            changes_made.append(f"respondent_name column: {str(e)}")
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Database schema updated successfully',
            'changes_made': changes_made
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Failed to update database schema: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@dashboard.route('/api/table-structure')
def check_table_structure():
    """Check the current structure of database tables"""
    try:
        from app import db
        
        table_info = {}
        
        # Check residents table structure
        try:
            result = db.session.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'residents' 
                ORDER BY ordinal_position
            """)
            residents_columns = [dict(row) for row in result]
            table_info['residents'] = residents_columns
        except Exception as e:
            table_info['residents'] = f"Error: {str(e)}"
        
        # Check households table structure
        try:
            result = db.session.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'households' 
                ORDER BY ordinal_position
            """)
            households_columns = [dict(row) for row in result]
            table_info['households'] = households_columns
        except Exception as e:
            table_info['households'] = f"Error: {str(e)}"
        
        # Check blotters table structure
        try:
            result = db.session.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'blotters' 
                ORDER BY ordinal_position
            """)
            blotters_columns = [dict(row) for row in result]
            table_info['blotters'] = blotters_columns
        except Exception as e:
            table_info['blotters'] = f"Error: {str(e)}"
        
        # Check clearances table structure
        try:
            result = db.session.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'clearances' 
                ORDER BY ordinal_position
            """)
            clearances_columns = [dict(row) for row in result]
            table_info['clearances'] = clearances_columns
        except Exception as e:
            table_info['clearances'] = f"Error: {str(e)}"
        
        return jsonify({
            'status': 'success',
            'table_structures': table_info
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Failed to check table structure: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@dashboard.route('/api/recreate-tables')
def recreate_tables():
    """Drop and recreate all tables with correct schema (WARNING: This will delete all data)"""
    try:
        from app import db
        
        # Drop all tables
        db.drop_all()
        
        # Create all tables with new schema
        db.create_all()
        
        return jsonify({
            'status': 'success',
            'message': 'All tables recreated successfully with correct schema',
            'warning': 'All existing data has been deleted'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Failed to recreate tables: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500
