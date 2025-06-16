from app.src import db, get_jakarta_time
from datetime import datetime

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=get_jakarta_time)
    updated_at = db.Column(db.DateTime, default=get_jakarta_time, onupdate=get_jakarta_time)

    def __repr__(self):
        return f'<Inventory {self.product_name}>'
