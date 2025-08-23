# Event Management System

A Flask-based event management system with admin/user role separation.

## Features

- **Admin System**: Create, edit, and delete events
- **User System**: Register and manage event registrations  
- **Authentication**: Secure login/logout with session management
- **Role-Based Access**: Separate interfaces for admins and users
- **Responsive Design**: Bootstrap dark theme interface
- **Event Management**: Full CRUD operations for events
- **Registration System**: Users can register for events with capacity limits

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-wtf gunicorn psycopg2-binary
   ```

2. **Set Environment Variables**:
   ```bash
   export DATABASE_URL="your_database_url"
   export SESSION_SECRET="your_secret_key"
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```
   Or with Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

4. **Access the Application**:
   - Open your browser to `http://localhost:5000`
   - Default admin login: `admin` / `admin123`

## Project Structure

- `app.py` - Flask application setup and configuration
- `models.py` - Database models (User, Event, Attendee)
- `routes.py` - Main application routes
- `auth_routes.py` - Authentication routes
- `forms.py` - WTForms form definitions
- `templates/` - Jinja2 HTML templates
- `static/` - CSS and JavaScript files

## User Roles

**Administrator**:
- Create, edit, and delete events
- View all attendee registrations
- Manage event capacity and details

**Regular User**:
- Browse and search events
- Register for events
- View personal registration history

## Database

The application uses PostgreSQL in production with automatic table creation on startup. A default admin user is created automatically if no users exist.


Remove-Item -Recurse -Force .venv
.venv\Scripts\activate
uv pip install -r pyproject.toml
python main.py# Event_Management_System
# Event_Management_System
