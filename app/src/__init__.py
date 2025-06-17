from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
import pytz
import os

db = SQLAlchemy()
login_manager = LoginManager()

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
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
    
    # Set database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'instance', 'inventory.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"Using database at: {db_path}")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login untuk mengakses halaman ini'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(id):
        from app.src.models.user import User
        return User.query.get(int(id))
    
    with app.app_context():
        # Import blueprints
        from app.src.routes.main import main
        from app.src.routes.restock import restock
        from app.src.routes.history import history
        from app.src.routes.auth import auth
        
        # Register blueprints
        app.register_blueprint(main)
        app.register_blueprint(restock)
        app.register_blueprint(history)
        app.register_blueprint(auth)
        
        # Create database tables
        db.create_all()
    
    return app