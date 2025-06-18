from app.src import create_app, db
from flask_migrate import Migrate
import sys

def upgrade_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Add new columns
            db.engine.execute('ALTER TABLE stock_history ADD COLUMN user_id INTEGER REFERENCES user(id);')
            db.engine.execute('ALTER TABLE stock_history ADD COLUMN stock_before INTEGER;')
            db.engine.execute('ALTER TABLE stock_history ADD COLUMN stock_after INTEGER;')
            
            print("Successfully added new columns to stock_history table")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            sys.exit(1)

if __name__ == "__main__":
    upgrade_database()
