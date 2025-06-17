from app.src import db, get_jakarta_time
from datetime import datetime

class StockHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'in' or 'out'
    quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)  # Price at time of transaction
    selling_price = db.Column(db.Float, nullable=False)  # Price at time of transaction
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=get_jakarta_time)
    reference = db.Column(db.String(100))  # For restock ID or sales reference
    status = db.Column(db.String(20), default='completed')  # completed, cancelled
    
    @property
    def total_value(self):
        """Calculate total value of transaction"""
        price = self.selling_price if self.type == 'out' else self.purchase_price
        return price * self.quantity
    
    @property
    def profit(self):
        """Calculate profit for out transactions"""
        if self.type == 'out' and self.status == 'completed':
            return (self.selling_price - self.purchase_price) * self.quantity
        return 0
    
    # Relationship with Inventory
    inventory = db.relationship('Inventory', backref=db.backref('history', lazy=True))

    def __repr__(self):
        return f'<StockHistory {self.type} {self.quantity} of {self.inventory.product_name}>'
