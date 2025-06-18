from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime
import pytz
import os

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

def create_app():
    app = Flask(__name__)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Roll back db session in case of error
        app.logger.error(f'Server Error: {error}', exc_info=True)
        return render_template('errors/500.html'), 500
    
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
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login untuk mengakses halaman ini'
    login_manager.login_message_category = 'warning'
    
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        
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
        from app.src.routes.statistics import statistics  # Add this line

        # Register blueprints
        app.register_blueprint(main)
        app.register_blueprint(restock)
        app.register_blueprint(history)
        app.register_blueprint(auth)
        app.register_blueprint(statistics)  # Add this line
    
    return app