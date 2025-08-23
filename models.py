from app import db
from datetime import datetime
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with events (for admin users)
    events = db.relationship('Event', backref='creator', lazy=True)
    # Relationship with attendee registrations
    registrations = db.relationship('Attendee', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(300), nullable=False)
    max_attendees = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship with attendees
    attendees = db.relationship('Attendee', backref='event', lazy=True, cascade='all, delete-orphan')
    
    @property
    def status(self):
        """Determine event status based on current date and time"""
        now = datetime.now()
        event_datetime = datetime.combine(self.date, self.time)
        
        if event_datetime > now:
            return 'upcoming'
        elif event_datetime.date() == now.date():
            return 'ongoing'
        else:
            return 'completed'
    
    @property
    def attendee_count(self):
        """Get current number of registered attendees"""
        return db.session.query(Attendee).filter_by(event_id=self.id).count()
    
    @property
    def available_spots(self):
        """Get number of available spots"""
        return self.max_attendees - self.attendee_count
    
    def __repr__(self):
        return f'<Event {self.name}>'

class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_attendee_per_event'),)
    
    def __repr__(self):
        return f'<Attendee {self.name} - Event {self.event_id}>'
