from app.src import db, get_jakarta_time
from datetime import datetime

class StockHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'in' or 'out'
    quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=get_jakarta_time)
    reference = db.Column(db.String(100))  # For restock ID or sales reference
    
    # Relationship with Inventory
    inventory = db.relationship('Inventory', backref=db.backref('history', lazy=True))

    def __repr__(self):
        return f'<StockHistory {self.type} {self.quantity} of {self.inventory.product_name}>'
