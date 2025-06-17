from app.src import db, get_jakarta_time
from datetime import datetime

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)  # Add default
    selling_price = db.Column(db.Float, nullable=False, default=0.0)  # Add default
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=get_jakarta_time)
    updated_at = db.Column(db.DateTime, default=get_jakarta_time, onupdate=get_jakarta_time)

    @property
    def inventory_value(self):
        """Calculate the total value of this inventory item"""
        return self.purchase_price * self.quantity
    
    @property
    def profit_margin(self):
        """Calculate the profit margin percentage"""
        if self.purchase_price > 0:
            return ((self.selling_price - self.purchase_price) / self.purchase_price) * 100
        return 0

    def __repr__(self):
        return f'<Inventory {self.product_name}>'
