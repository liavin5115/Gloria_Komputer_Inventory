from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.src.models.inventory import Inventory
from app.src.models.restock import Restock
from app.src.models.stock_history import StockHistory
from app.src import db
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
def index():
    total_products = Inventory.query.count()
    low_stock = Inventory.query.filter(Inventory.quantity < 5).count()
    categories = db.session.query(Inventory.category).distinct().count()
    pending_restocks = Restock.query.filter_by(status='pending').count()
    
    # Get low stock items for the dashboard
    low_stock_items = Inventory.query.filter(Inventory.quantity < 5).all()
    
    # Get recent activities
    recent_activities = StockHistory.query.order_by(StockHistory.date.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_products=total_products,
                         low_stock=low_stock,
                         categories=categories,
                         pending_restocks=pending_restocks,
                         low_stock_items=low_stock_items,
                         recent_activities=recent_activities)

@main.route('/inventory')
def inventory_list():
    # Get all categories for the filter dropdown
    categories = db.session.query(Inventory.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]  # Remove None/empty categories
    
    # Get inventory items and convert to dict for JSON serialization
    inventory_items = [{
        'id': item.id,
        'product_name': item.product_name,
        'description': item.description,
        'quantity': item.quantity,
        'price': item.price,
        'category': item.category,
    } for item in Inventory.query.all()]
    
    return render_template('inventory/list.html', 
                         inventory_items=inventory_items,
                         categories=categories)

@main.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory():
    if request.method == 'POST':
        new_item = Inventory(
            product_name=request.form['product_name'],
            description=request.form['description'],
            quantity=int(request.form['quantity']),
            price=float(request.form['price']),
            category=request.form['category']
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('main.inventory_list'))
    return render_template('inventory/form.html', item=None)

@main.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
def edit_inventory(id):
    item = Inventory.query.get_or_404(id)
    if request.method == 'POST':
        item.product_name = request.form['product_name']
        item.description = request.form['description']
        item.quantity = int(request.form['quantity'])
        item.price = float(request.form['price'])
        item.category = request.form['category']
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('main.inventory_list'))
    return render_template('inventory/form.html', item=item)

@main.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    item = Inventory.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@main.route('/inventory/<int:id>/stock-out', methods=['POST'])
def stock_out(id):
    item = Inventory.query.get_or_404(id)
    data = request.get_json()
    quantity = int(data['quantity'])
    
    # Validate quantity
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be positive'}), 400
    if quantity > item.quantity:
        return jsonify({'error': 'Not enough stock available'}), 400
    
    # Update inventory quantity
    item.quantity -= quantity
    
    # Create stock history record
    history = StockHistory(
        inventory_id=item.id,
        type='out',
        quantity=quantity,
        reference=data.get('reference', ''),
        notes=data.get('notes', '')
    )
    
    db.session.add(history)
    db.session.commit()
    
    flash('Stock out recorded successfully!', 'success')
    return jsonify({'success': True})
