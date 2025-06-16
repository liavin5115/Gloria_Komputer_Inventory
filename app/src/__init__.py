from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import pytz
from datetime import datetime

db = SQLAlchemy()

def get_jakarta_time():
    """Get current time in Jakarta timezone (UTC+7)"""
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    return datetime.now(pytz.UTC).astimezone(jakarta_tz)

def utc_to_local(utc_dt):
    """Convert UTC datetime to Jakarta timezone"""
    if utc_dt is None:
        return None
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    return utc_dt.astimezone(jakarta_tz)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # Set database path to app directory
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'instance', 'inventory.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"Using database at: {db_path}")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Import and register blueprints
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Continue anyway to allow for database setup

        # Register blueprints
        from .routes import main, restock, history
        app.register_blueprint(main)
        app.register_blueprint(restock)
        app.register_blueprint(history)
        
    return app