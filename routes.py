from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import app, db
from models import Event, Attendee, User
from forms import EventForm, EditEventForm, AttendeeForm
from datetime import datetime
from sqlalchemy import or_
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Display all events with search and filter functionality"""
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    
    query = Event.query
    
    # Apply search filter
    if search:
        query = query.filter(
            or_(
                Event.name.contains(search),
                Event.description.contains(search),
                Event.location.contains(search)
            )
        )
    
    # Get all events first, then filter by status in Python since it's a property
    all_events = query.order_by(Event.date.desc(), Event.time.desc()).all()
    
    # Filter by status if specified
    if status_filter != 'all':
        all_events = [event for event in all_events if event.status == status_filter]
    
    return render_template('index.html', 
                         events=all_events, 
                         search=search, 
                         status_filter=status_filter)

@app.route('/create_event', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    """Create a new event"""
    form = EventForm()
    
    if form.validate_on_submit():
        try:
            event = Event(
                name=form.name.data,
                description=form.description.data,
                date=form.date.data,
                time=form.time.data,
                location=form.location.data,
                max_attendees=form.max_attendees.data,
                created_by=current_user.id
            )
            
            db.session.add(event)
            db.session.commit()
            
            flash(f'Event "{event.name}" created successfully!', 'success')
            return redirect(url_for('event_detail', id=event.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the event. Please try again.', 'danger')
            app.logger.error(f'Error creating event: {str(e)}')
    
    return render_template('create_event.html', form=form)

@app.route('/event/<int:id>')
def event_detail(id):
    """Display event details"""
    event = Event.query.get_or_404(id)
    return render_template('event_detail.html', event=event)

@app.route('/event/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(id):
    """Edit an existing event"""
    event = Event.query.get_or_404(id)
    form = EditEventForm(obj=event)
    
    if form.validate_on_submit():
        try:
            # Check if reducing max_attendees would exceed current registrations
            if form.max_attendees.data < event.attendee_count:
                flash(f'Cannot reduce maximum attendees below current registrations ({event.attendee_count}).', 'warning')
                return render_template('edit_event.html', form=form, event=event)
            
            form.populate_obj(event)
            event.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash(f'Event "{event.name}" updated successfully!', 'success')
            return redirect(url_for('event_detail', id=event.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the event. Please try again.', 'danger')
            app.logger.error(f'Error updating event: {str(e)}')
    
    return render_template('edit_event.html', form=form, event=event)

@app.route('/event/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(id):
    """Delete an event"""
    event = Event.query.get_or_404(id)
    
    try:
        event_name = event.name
        db.session.delete(event)
        db.session.commit()
        
        flash(f'Event "{event_name}" deleted successfully!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the event. Please try again.', 'danger')
        app.logger.error(f'Error deleting event: {str(e)}')
        return redirect(url_for('event_detail', id=id))

@app.route('/event/<int:id>/register', methods=['GET', 'POST'])
@login_required
def register_for_event(id):
    """Register for an event"""
    event = Event.query.get_or_404(id)
    form = AttendeeForm()
    
    # Check if event is full
    if event.available_spots <= 0:
        flash('Sorry, this event is fully booked.', 'warning')
        return redirect(url_for('event_detail', id=id))
    
    # Check if event has already passed
    if event.status == 'completed':
        flash('Cannot register for a completed event.', 'warning')
        return redirect(url_for('event_detail', id=id))
    
    if form.validate_on_submit():
        try:
            # Check if user is already registered
            existing_attendee = Attendee.query.filter_by(
                user_id=current_user.id, 
                event_id=event.id
            ).first()
            
            if existing_attendee:
                flash('You are already registered for this event.', 'info')
                return redirect(url_for('event_detail', id=id))
            
            # Check available spots again (race condition protection)
            if event.available_spots <= 0:
                flash('Sorry, this event just became fully booked.', 'warning')
                return redirect(url_for('event_detail', id=id))
            
            attendee = Attendee(
                name=form.name.data,
                email=current_user.email,
                phone=form.phone.data,
                event_id=event.id,
                user_id=current_user.id
            )
            
            db.session.add(attendee)
            db.session.commit()
            
            flash(f'Successfully registered for "{event.name}"!', 'success')
            return redirect(url_for('event_detail', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            app.logger.error(f'Error registering attendee: {str(e)}')
    
    return render_template('register.html', form=form, event=event)

@app.route('/event/<int:event_id>/attendee/<int:attendee_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_attendee(event_id, attendee_id):
    """Remove an attendee from an event"""
    event = Event.query.get_or_404(event_id)
    attendee = Attendee.query.get_or_404(attendee_id)
    
    # Verify attendee belongs to this event
    if attendee.event_id != event.id:
        abort(404)
    
    try:
        attendee_name = attendee.name
        db.session.delete(attendee)
        db.session.commit()
        
        flash(f'Removed {attendee_name} from the event.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while removing the attendee. Please try again.', 'danger')
        app.logger.error(f'Error removing attendee: {str(e)}')
    
    return redirect(url_for('event_detail', id=event_id))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
