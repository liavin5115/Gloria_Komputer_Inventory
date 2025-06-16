from app.src import create_app, db
from app.src.models.inventory import Inventory
import os
import sqlite3

def init_db(app):
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Check if database exists and is valid
        try:
            if os.path.exists(db_path):
                # Test if database is valid
                conn = sqlite3.connect(db_path)
                conn.execute('SELECT * FROM inventory LIMIT 1')
                conn.close()
                print("Using existing database")
                return
        except Exception as e:
            print(f"Error checking database: {e}")
            print("Creating new database...")
        
        # Create new database if needed
        try:
            db.create_all()
            print("Database tables created successfully")
            
            if not Inventory.query.first():
                sample_items = [
                    Inventory(
                        product_name='Laptop ASUS ROG',
                        description='Gaming laptop with RTX 3060',
                        quantity=5,
                        price=15000000,
                        category='Laptop'
                    ),
                    Inventory(
                        product_name='Mouse Logitech G502',
                        description='Gaming mouse with RGB',
                        quantity=10,
                        price=899000,
                        category='Peripherals'
                    )
                ]
                db.session.bulk_save_objects(sample_items)
                db.session.commit()
                print("Sample data created successfully")
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