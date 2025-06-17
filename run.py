from app.src import create_app, db
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

app = create_app()

def init_db():
    with app.app_context():
        try:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            logging.info(f"Using database at: {db_path}")
            
            if os.path.exists(db_path):
                db.engine.connect()
                logging.info("Database connection successful")
            
            db.create_all()
            logging.info("Database tables created successfully")
            
        except Exception as e:
            logging.error(f"Database initialization error: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    try:
        init_db()
        debug = os.environ.get('FLASK_ENV') == 'development'
        logging.info(f"Starting application in {'development' if debug else 'production'} mode")
        app.run(debug=debug, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Application error: {str(e)}", exc_info=True)
        raise