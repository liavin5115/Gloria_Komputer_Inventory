from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.src.models.inventory import Inventory
from app.src.models.restock import Restock
from app.src.models.stock_history import StockHistory
from app.src import db, get_jakarta_time  # Add get_jakarta_time import
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Get total products and inventory value
    inventory_stats = db.session.query(
        func.count(Inventory.id).label('total_products'),
        func.sum(Inventory.quantity * Inventory.purchase_price).label('total_inventory_value')
    ).first()
    
    total_products = inventory_stats.total_products
    total_inventory_value = inventory_stats.total_inventory_value or 0
    
    # Get products with low stock (less than 5)
    low_stock = Inventory.query.filter(Inventory.quantity < 5).count()
    
    # Get distinct categories count
    categories = db.session.query(Inventory.category).distinct().count()
    
    # Get pending restock count
    pending_restocks = Restock.query.filter_by(status='pending').count()
    
    # Calculate sales metrics
    today = get_jakarta_time().date()
    month_start = today.replace(day=1)
    
    # Daily sales
    daily_sales = db.session.query(
        func.sum(StockHistory.quantity * StockHistory.selling_price)
    ).filter(
        StockHistory.type == 'out',
        StockHistory.status == 'completed',
        func.date(StockHistory.date) == today
    ).scalar() or 0
    
    # Monthly sales
    monthly_sales = db.session.query(
        func.sum(StockHistory.quantity * StockHistory.selling_price)
    ).filter(
        StockHistory.type == 'out',
        StockHistory.status == 'completed',
        func.date(StockHistory.date) >= month_start
    ).scalar() or 0
    
    # Calculate profits
    daily_profit = db.session.query(
        func.sum((StockHistory.selling_price - StockHistory.purchase_price) * StockHistory.quantity)
    ).filter(
        StockHistory.type == 'out',
        StockHistory.status == 'completed',
        func.date(StockHistory.date) == today
    ).scalar() or 0
    
    monthly_profit = db.session.query(
        func.sum((StockHistory.selling_price - StockHistory.purchase_price) * StockHistory.quantity)
    ).filter(
        StockHistory.type == 'out',
        StockHistory.status == 'completed',
        func.date(StockHistory.date) >= month_start
    ).scalar() or 0
      # Get products with low stock for warning display
    low_stock_items = Inventory.query.filter(Inventory.quantity < 5).all()
    
    return render_template('index.html',
                         total_products=total_products,
                         low_stock=low_stock,
                         categories=categories,
                         pending_restocks=pending_restocks,
                         low_stock_items=low_stock_items,
                         total_inventory_value=total_inventory_value,
                         daily_sales=daily_sales,
                         monthly_sales=monthly_sales,
                         daily_profit=daily_profit,
                         monthly_profit=monthly_profit)
    
    return render_template('index.html',
                         total_products=total_products,
                         low_stock=low_stock,
                         categories=categories,
                         pending_restocks=pending_restocks,
                         low_stock_items=low_stock_items)
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
@login_required
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
        'purchase_price': item.purchase_price,
        'selling_price': item.selling_price,
        'category': item.category
    } for item in Inventory.query.all()]
    
    return render_template('inventory/list.html', 
                         inventory_items=inventory_items,
                         categories=categories)

@main.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if request.method == 'POST':
        try:
            # Validate that selling price is not less than purchase price
            purchase_price = request.form.get('purchase_price', type=float)
            selling_price = request.form.get('selling_price', type=float)
            
            if selling_price < purchase_price:
                flash('Error: Harga jual tidak boleh lebih rendah dari harga beli', 'danger')
                return redirect(url_for('main.add_inventory'))
            
            inventory = Inventory(
                product_name=request.form.get('product_name'),
                description=request.form.get('description'),
                quantity=request.form.get('quantity', type=int),
                purchase_price=purchase_price,
                selling_price=selling_price,
                category=request.form.get('category')
            )
            
            db.session.add(inventory)
            db.session.commit()
            
            flash('Produk berhasil ditambahkan', 'success')
            return redirect(url_for('main.inventory_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('main.add_inventory'))
    
    return render_template('inventory/form.html')

@main.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(id):
    inventory = Inventory.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Validate that selling price is not less than purchase price
            purchase_price = request.form.get('purchase_price', type=float)
            selling_price = request.form.get('selling_price', type=float)
            
            if selling_price < purchase_price:
                flash('Error: Harga jual tidak boleh lebih rendah dari harga beli', 'danger')
                return redirect(url_for('main.edit_inventory', id=id))
            
            inventory.product_name = request.form.get('product_name')
            inventory.description = request.form.get('description')
            inventory.quantity = request.form.get('quantity', type=int)
            inventory.purchase_price = purchase_price
            inventory.selling_price = selling_price
            inventory.category = request.form.get('category')
            
            db.session.commit()
            flash('Produk berhasil diperbarui', 'success')
            return redirect(url_for('main.inventory_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('main.edit_inventory', id=id))
    
    return render_template('inventory/form.html', item=inventory)

@main.route('/inventory/<int:id>', methods=['DELETE'])
@login_required
def delete_inventory(id):
    try:
        inventory = Inventory.query.get_or_404(id)
        db.session.delete(inventory)
        db.session.commit()
        return jsonify({'message': 'Produk berhasil dihapus'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main.route('/inventory/<int:id>/stock-out', methods=['POST'])
@login_required
def stock_out(id):
    try:
        quantity = request.form.get('quantity', type=int)
        if not quantity or quantity < 1:
            return jsonify({'error': 'Jumlah tidak valid'}), 400
            
        inventory = Inventory.query.get_or_404(id)
        if quantity > inventory.quantity:
            return jsonify({'error': 'Stok tidak mencukupi'}), 400
            
        inventory.quantity -= quantity
          # Create stock history
        history = StockHistory(
            inventory_id=id,
            type='out',
            quantity=quantity,
            notes=request.form.get('notes'),
            status='completed',
            purchase_price=inventory.purchase_price,
            selling_price=inventory.selling_price
        )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'message': 'Stok berhasil dikurangi',
            'new_quantity': inventory.quantity
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
