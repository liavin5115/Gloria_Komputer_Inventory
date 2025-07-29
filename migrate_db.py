from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Set database path from environment variable or default
db_path = os.environ.get('DATABASE_URL', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'inventory.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def migrate_database():
    with app.app_context():
        try:
            # Add new columns
            db.engine.execute('ALTER TABLE stock_history ADD COLUMN user_id INTEGER REFERENCES user(id);')
            print("Added user_id column")
            
            db.engine.execute('ALTER TABLE stock_history ADD COLUMN stock_before INTEGER;')
            print("Added stock_before column")
            
            db.engine.execute('ALTER TABLE stock_history ADD COLUMN stock_after INTEGER;')
            print("Added stock_after column")
            
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            
if __name__ == "__main__":
    migrate_database()
