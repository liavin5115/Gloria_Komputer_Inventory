from app.src import create_app, db
from app.src.models.inventory import Inventory
import os

def main():
    try:
        # Create the Flask application
        app = create_app()
        
        with app.app_context():
            # Ensure database exists
            db.create_all()
            
            # Create sample data if database is empty
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
        
        # Run the application
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error starting application: {e}")
        raise

if __name__ == "__main__":
    main()