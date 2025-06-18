from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.src.models.restock import Restock
from app.src.models.inventory import Inventory
from app.src.models.stock_history import StockHistory
from app.src import db, get_jakarta_time
from datetime import datetime, timedelta
from sqlalchemy import and_

restock = Blueprint('restock', __name__)

@restock.route('/restock')
def restock_list():
    today = get_jakarta_time().date()
    
    # Get counts for summary cards
    pending_count = Restock.query.filter_by(status='pending').count()
    due_today_count = Restock.query.filter(
        and_(
            Restock.status == 'pending',
            Restock.expected_date == today
        )
    ).count()
    completed_count = Restock.query.filter_by(status='received').count()  # Add this line
    
    # Get items by status
    pending_items = Restock.query.filter_by(status='pending').order_by(Restock.expected_date).all()
    completed_items = Restock.query.filter_by(status='received').order_by(Restock.updated_at.desc()).all()
    cancelled_items = Restock.query.filter_by(status='cancelled').order_by(Restock.updated_at.desc()).all()
    
    return render_template('restock/list.html',
                         pending_items=pending_items,
                         completed_items=completed_items,
                         cancelled_items=cancelled_items,
                         pending_count=pending_count,
                         due_today_count=due_today_count,
                         completed_count=completed_count,  # Add this line
                         today=today)

@restock.route('/restock/add', methods=['GET', 'POST'])
def add_restock():
    if request.method == 'POST':
        expected_date = datetime.strptime(request.form['expected_date'], '%Y-%m-%d').date()
        new_item = Restock(
            product_name=request.form['product_name'],
            description=request.form['description'],
            quantity=int(request.form['quantity']),
            price=float(request.form['price']),
            category=request.form['category'],
            expected_date=expected_date,
            supplier=request.form['supplier']
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Restock item added successfully!', 'success')
        return redirect(url_for('restock.restock_list'))
    
    # Get all inventory items for the product selection
    inventory_items = Inventory.query.order_by(Inventory.product_name).all()
    return render_template('restock/form.html', inventory_items=inventory_items, item=None)

@restock.route('/restock/<int:id>/receive', methods=['POST'])
def receive_restock(id):
    restock_item = Restock.query.get_or_404(id)
    
    # Check if item exists in inventory
    inventory_item = Inventory.query.filter_by(product_name=restock_item.product_name).first()
    
    if inventory_item:
        # Update existing inventory item
        inventory_item.quantity += restock_item.quantity
        old_purchase_price = inventory_item.purchase_price
        inventory_item.purchase_price = restock_item.price  # Update purchase price with latest
        
        # Maintain the same profit margin when updating purchase price
        if old_purchase_price > 0:  # Avoid division by zero
            margin = (inventory_item.selling_price - old_purchase_price) / old_purchase_price
            inventory_item.selling_price = restock_item.price * (1 + margin)
    else:
        # Create new inventory item
        inventory_item = Inventory(
            product_name=restock_item.product_name,
            description=restock_item.description,
            quantity=restock_item.quantity,
            purchase_price=restock_item.price,
            selling_price=restock_item.price * 1.2,  # Set default 20% markup
            category=restock_item.category
        )
        db.session.add(inventory_item)
        db.session.flush()  # Get the ID of the new inventory item
    
    # Create stock history record
    history = StockHistory(
        inventory_id=inventory_item.id,
        type='in',
        quantity=restock_item.quantity,
        purchase_price=restock_item.price,
        selling_price=inventory_item.selling_price,
        status='completed',
        reference=f'Restock #{restock_item.id}',
        notes=f'Received from supplier: {restock_item.supplier}'
    )
    db.session.add(history)
    
    # Update restock status
    restock_item.status = 'received'
    db.session.commit()
    
    flash('Restock item received and inventory updated!', 'success')
    return redirect(url_for('restock.restock_list'))

@restock.route('/restock/<int:id>/cancel', methods=['POST'])
def cancel_restock(id):
    restock_item = Restock.query.get_or_404(id)
    restock_item.status = 'cancelled'
    db.session.commit()
    flash('Restock order cancelled successfully', 'success')
    return jsonify({'success': True})
