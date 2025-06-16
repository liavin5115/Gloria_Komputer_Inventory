from app.src import create_app, db
from app.src.models.inventory import Inventory

def init_db():
    app = create_app()
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("Database tables created successfully")
            
            # Add sample data if database is empty
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

if __name__ == "__main__":
    init_db()
