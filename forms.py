from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, IntegerField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo, ValidationError
from datetime import date

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[
        DataRequired(message="Event name is required"),
        Length(min=3, max=200, message="Event name must be between 3 and 200 characters")
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000, message="Description cannot exceed 1000 characters")
    ])
    
    date = DateField('Event Date', validators=[
        DataRequired(message="Event date is required")
    ], default=date.today)
    
    time = TimeField('Event Time', validators=[
        DataRequired(message="Event time is required")
    ])
    
    location = StringField('Location', validators=[
        DataRequired(message="Location is required"),
        Length(min=5, max=300, message="Location must be between 5 and 300 characters")
    ])
    
    max_attendees = IntegerField('Maximum Attendees', validators=[
        DataRequired(message="Maximum attendees is required"),
        NumberRange(min=1, max=10000, message="Maximum attendees must be between 1 and 10,000")
    ], default=100)
    
    submit = SubmitField('Create Event')

class EditEventForm(EventForm):
    submit = SubmitField('Update Event')

class AttendeeForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(message="Name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20, message="Phone number cannot exceed 20 characters")
    ])
    
    submit = SubmitField('Register for Event')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters")
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters")
    ])
    
    email = StringField('Email Address', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120, message="Email cannot exceed 120 characters")
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])
    
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')
