#!/bin/sh
set -e

echo "Checking database directory..."
DB_DIR=${DATABASE_PATH:-/data/instance}
DB_DIR=$(dirname "$DB_DIR")

mkdir -p "$DB_DIR"
chmod 777 "$DB_DIR"

echo "Initializing database..."
python <<EOF
from app.src import create_app, db
from app.src.models.inventory import Inventory

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("Database tables created")
        
        # Add sample data if empty
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
            print("Sample data created")
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("Will continue anyway to allow for database setup...")
EOF

echo "Starting Gunicorn..."
exec gunicorn \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --bind ${GUNICORN_BIND:-0.0.0.0:5000} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --env DATABASE_PATH="$DB_DIR/inventory.db" \
    "run:app"
