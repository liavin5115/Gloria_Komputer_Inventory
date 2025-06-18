from app.src import create_app, db
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

app = create_app()

if __name__ == "__main__":
    try:
        with app.app_context():
            # Ensure instance directory exists
            os.makedirs('instance', exist_ok=True)
            
            # Initialize database
            db.create_all()
            logging.info("Database initialized successfully")
            
        debug = os.environ.get('FLASK_ENV') == 'development'
        app.run(debug=debug, host='0.0.0.0', port=5000)
        
    except Exception as e:
        logging.error(f"Error: {str(e)}", exc_info=True)