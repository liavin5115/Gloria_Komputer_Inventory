from flask_migrate import Migrate, upgrade
from app.src import create_app, db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        upgrade()
