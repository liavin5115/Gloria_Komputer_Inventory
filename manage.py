from flask.cli import FlaskGroup
from app.src import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(app)

@cli.command('recreate_db')
def recreate_db():
    """Recreates the database."""
    with app.app_context():
        print("Dropping existing database...")
        db.drop_all()
        print("Creating new database...")
        db.create_all()
        print("Done!")

if __name__ == '__main__':
    cli()
