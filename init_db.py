import os
import logging
from app.src import create_app, db
from app.src.models.inventory import Inventory
from app.src.models.user import User
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    app = create_app()
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Add admin user if no users exist
            if not User.query.first():
                admin = User(
                    username='admin',
                    name='Administrator',
                    role='admin'
                )
                admin.password_hash = generate_password_hash('admin123')  # Change this password in production
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully")
            
            return True
                
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            return False

if __name__ == "__main__":
    success = init_db()
    exit(0 if success else 1)
