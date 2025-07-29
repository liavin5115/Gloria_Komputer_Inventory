from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime
import pytz
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_jakarta_time():
    """Get current time in Jakarta timezone (UTC+7)"""
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    return datetime.now(pytz.UTC).astimezone(jakarta_tz)

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def utc_to_local(utc_dt):
    """Convert UTC datetime to Jakarta timezone"""
    if utc_dt is None:
        return None
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    return utc_dt.astimezone(jakarta_tz)

def init_database(app):
    """Initialize database with proper error handling"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def create_app():
    app = Flask(__name__)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Roll back db session in case of error
        logger.error(f'Server Error: {error}', exc_info=True)
        return render_template('errors/500.html'), 500
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # Set database path from environment variable or default
    db_path = os.environ.get(
        'DATABASE_URL',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'inventory.db')
    )
    data_dir = os.path.dirname(db_path)
    
    try:
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"Using database at: {db_path}")
    except Exception as e:
        logger.error(f"Failed to create database directory: {str(e)}")
        raise

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login untuk mengakses halaman ini'
    login_manager.login_message_category = 'warning'
    
    init_database(app)
    
    @login_manager.user_loader
    def load_user(id):
        from app.src.models.user import User
        return User.query.get(int(id))
    
    with app.app_context():
        # Import all blueprints from routes
        from app.src.routes import __all__ as blueprint_names
        from app.src import routes
        for name in blueprint_names:
            app.register_blueprint(getattr(routes, name))
    return app