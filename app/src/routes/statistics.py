from flask import Blueprint, render_template
from app.src.models.inventory import Inventory
from app.src.models.stock_history import StockHistory
from app.src import db, get_jakarta_time
from sqlalchemy import func
from datetime import datetime, timedelta

statistics = Blueprint('statistics', __name__)

@statistics.route('/statistics')
def index():
    # Get date range (last 30 days)
    end_date = get_jakarta_time()
    start_date = end_date - timedelta(days=30)
    
    # Calculate total profit
    total_profit = db.session.query(
        func.sum((StockHistory.selling_price - StockHistory.purchase_price) * StockHistory.quantity)
    ).filter(
        StockHistory.type == 'out',
        StockHistory.status == 'completed'
    ).scalar() or 0

    # Calculate total inventory value
    total_inventory_value = db.session.query(
        func.sum(Inventory.quantity * Inventory.purchase_price)
    ).scalar() or 0

    # Calculate total sales
    total_sales = db.session.query(
        func.sum(StockHistory.selling_price * StockHistory.quantity)
    ).filter(
        StockHistory.type == 'out',
        StockHistory.status == 'completed'
    ).scalar() or 0

    # Calculate total expenses (purchases)
    total_expenses = db.session.query(
        func.sum(StockHistory.purchase_price * StockHistory.quantity)
    ).filter(
        StockHistory.type == 'in',
        StockHistory.status == 'completed'
    ).scalar() or 0

    # Get daily sales and profit data
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        daily_sale = db.session.query(
            func.sum(StockHistory.selling_price * StockHistory.quantity)
        ).filter(
            StockHistory.type == 'out',
            StockHistory.status == 'completed',
            StockHistory.date >= current_date,
            StockHistory.date < next_date
        ).scalar() or 0
        
        daily_profit = db.session.query(
            func.sum((StockHistory.selling_price - StockHistory.purchase_price) * StockHistory.quantity)
        ).filter(
            StockHistory.type == 'out',
            StockHistory.status == 'completed',
            StockHistory.date >= current_date,
            StockHistory.date < next_date
        ).scalar() or 0
        
        daily_stats.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'sales': daily_sale,
            'profit': daily_profit
        })
        current_date = next_date

    # Get category distribution
    category_stats = db.session.query(
        Inventory.category,
        func.count(Inventory.id)
    ).group_by(Inventory.category).all()

    # Get top products
    top_products = db.session.query(
        Inventory,
        func.sum(StockHistory.quantity).label('total_sold'),
        func.sum((StockHistory.selling_price - StockHistory.purchase_price) * StockHistory.quantity).label('total_profit')
    ).join(
        StockHistory,
        StockHistory.inventory_id == Inventory.id
    ).filter(
        StockHistory.type == 'out',
        StockHistory.status == 'completed'
    ).group_by(
        Inventory
    ).order_by(
        func.sum(StockHistory.quantity).desc()
    ).limit(10).all()

    return render_template('statistics/index.html',
        total_profit=total_profit,
        total_inventory_value=total_inventory_value,
        total_sales=total_sales,
        total_expenses=total_expenses,
        profit_percentage=min(100, (total_profit / total_sales * 100) if total_sales > 0 else 0),
        inventory_percentage=100,
        sales_percentage=min(100, (total_sales / (total_sales + total_inventory_value) * 100) if (total_sales + total_inventory_value) > 0 else 0),
        expenses_percentage=min(100, (total_expenses / total_sales * 100) if total_sales > 0 else 0),
        dates=[stat['date'] for stat in daily_stats],
        sales_data=[stat['sales'] for stat in daily_stats],
        profit_data=[stat['profit'] for stat in daily_stats],
        category_labels=[cat[0] for cat in category_stats],
        category_data=[cat[1] for cat in category_stats],
        top_products=[{
            'product_name': product.product_name,
            'category': product.category,
            'total_sold': total_sold,
            'total_profit': total_profit,
            'quantity': product.quantity
        } for product, total_sold, total_profit in top_products]
    )
