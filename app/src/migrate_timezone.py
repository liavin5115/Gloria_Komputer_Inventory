from app.src import create_app, db, utc_to_local
from app.src.models.stock_history import StockHistory
from app.src.models.inventory import Inventory
from app.src.models.restock import Restock
import pytz

def migrate_timestamps():
    app = create_app()
    with app.app_context():
        # Migrate Stock History dates
        histories = StockHistory.query.all()
        for history in histories:
            if history.date:
                history.date = utc_to_local(history.date)
        
        # Migrate Inventory timestamps
        inventory_items = Inventory.query.all()
        for item in inventory_items:
            if item.created_at:
                item.created_at = utc_to_local(item.created_at)
            if item.updated_at:
                item.updated_at = utc_to_local(item.updated_at)
        
        # Migrate Restock timestamps
        restock_items = Restock.query.all()
        for item in restock_items:
            if item.created_at:
                item.created_at = utc_to_local(item.created_at)
            if item.updated_at:
                item.updated_at = utc_to_local(item.updated_at)
        
        # Commit all changes
        db.session.commit()
        print("Successfully migrated timestamps to Asia/Jakarta timezone (UTC+7)")

if __name__ == "__main__":
    migrate_timestamps()
