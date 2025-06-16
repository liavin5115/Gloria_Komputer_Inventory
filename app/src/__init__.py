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
    
    # Ensure instance folder exists
    try:
        instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        # Set database path and ensure it's absolute
        db_path = os.path.join(instance_path, 'inventory.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        print(f"Database path: {db_path}")  # Debug print
        
        # Initialize extensions
        db.init_app(app)
        
        with app.app_context():
            # Import models to ensure they're registered
            from .models.inventory import Inventory
            from .models.restock import Restock
            from .models.stock_history import StockHistory
            
            # Create database tables
            try:
                db.create_all()
                print("Database tables created successfully")
            except Exception as e:
                print(f"Error creating database tables: {e}")
                raise
        
        # Register blueprints
        from .routes import main, restock, history
        app.register_blueprint(main)
        app.register_blueprint(restock)
        app.register_blueprint(history)
        
    except Exception as e:
        print(f"Error during app initialization: {e}")
        raise
    
    return app