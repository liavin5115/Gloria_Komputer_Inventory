from app.src import create_app, db
from app.src.models.inventory import Inventory
import os

def init_db(app):
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Check if database exists and is valid
        try:
            if os.path.exists(db_path):
                # Test if database is valid
                db.engine.connect()
                print("Database connection successful")
        except Exception as e:
            print(f"Error checking database: {e}")
            print("Creating new database...")
        
        # Create new database if needed
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

app = create_app()

if __name__ == "__main__":
    try:
        init_db(app)
        debug = os.environ.get('FLASK_ENV') == 'development'
        app.run(debug=debug, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting application: {e}")
        raise