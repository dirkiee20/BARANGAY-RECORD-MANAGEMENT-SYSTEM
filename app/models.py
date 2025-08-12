from datetime import datetime
from app import db


class Household(db.Model):
    __tablename__ = 'households'

    id = db.Column(db.Integer, primary_key=True)
    head_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    purok = db.Column(db.String(50), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    residents = db.relationship('Resident', back_populates='household', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Household id={self.id} head={self.head_name!r}>'


class Resident(db.Model):
    __tablename__ = 'residents'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=False)
    alias = db.Column(db.String(80), nullable=True)
    place_of_birth = db.Column(db.String(255), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    civil_status = db.Column(db.String(20), nullable=True)
    purok = db.Column(db.String(50), nullable=True)
    voters_status = db.Column(db.String(20), nullable=True)
    identified_as = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    occupation = db.Column(db.String(120), nullable=True)
    citizenship = db.Column(db.String(50), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    sex = db.Column(db.String(10), nullable=True)
    address = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(30), default='Active', nullable=False)

    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=True)
    household = db.relationship('Household', back_populates='residents')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    clearances = db.relationship('Clearance', back_populates='resident', cascade='all, delete-orphan')
    blotters_reported = db.relationship('Blotter', back_populates='reported_by', foreign_keys='Blotter.reported_by_id')

    def __repr__(self) -> str:
        return f'<Resident id={self.id} name={self.last_name}, {self.first_name}>'


class Blotter(db.Model):
    __tablename__ = 'blotters'

    id = db.Column(db.Integer, primary_key=True)
    case_title = db.Column(db.String(180), nullable=False)
    case_type = db.Column(db.String(50), nullable=True)
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='Open', nullable=False)
    location = db.Column(db.String(120), nullable=True)
    respondent_name = db.Column(db.String(120), nullable=True)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    hearing_date = db.Column(db.DateTime, nullable=True)

    reported_by_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=True)
    reported_by = db.relationship('Resident', back_populates='blotters_reported', foreign_keys=[reported_by_id])

    def __repr__(self) -> str:
        return f'<Blotter id={self.id} title={self.case_title!r} status={self.status}>'


class Clearance(db.Model):
    __tablename__ = 'clearances'

    id = db.Column(db.Integer, primary_key=True)
    clearance_type = db.Column(db.String(80), nullable=False)  # e.g., Barangay Clearance, Indigency
    purpose = db.Column(db.String(180), nullable=True)
    status = db.Column(db.String(30), default='Pending', nullable=False)
    issued_at = db.Column(db.DateTime, nullable=True)

    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=False)
    resident = db.relationship('Resident', back_populates='clearances')

    def __repr__(self) -> str:
        return f'<Clearance id={self.id} type={self.clearance_type!r} status={self.status}>'


class Official(db.Model):
    __tablename__ = 'officials'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(80), nullable=False)
    term_start = db.Column(db.Date, nullable=True)
    term_end = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='Active', nullable=False)

    def __repr__(self) -> str:
        return f'<Official id={self.id} {self.position} {self.full_name!r}>'
