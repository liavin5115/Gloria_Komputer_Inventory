from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.src.models.inventory import Inventory
from app.src.models.restock import Restock
from app.src.models.stock_history import StockHistory
from app.src import db
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # Get total products
    total_products = Inventory.query.count()
    
    # Get products with low stock (less than 5)
    low_stock = Inventory.query.filter(Inventory.quantity < 5).count()
    
    # Get distinct categories count
    categories = db.session.query(Inventory.category).distinct().count()
    
    # Get pending restock count
    pending_restocks = Restock.query.filter_by(status='pending').count()
    
    # Get products with low stock for warning display
    low_stock_items = Inventory.query.filter(Inventory.quantity < 5).all()
    
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
        'price': item.price,
        'category': item.category,
    } for item in Inventory.query.all()]
    
    return render_template('inventory/list.html', 
                         inventory_items=inventory_items,
                         categories=categories)

@main.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if request.method == 'POST':
        try:
            inventory = Inventory(
                product_name=request.form.get('product_name'),
                description=request.form.get('description'),
                quantity=request.form.get('quantity', type=int),
                price=request.form.get('price', type=float),
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
            inventory.product_name = request.form.get('product_name')
            inventory.description = request.form.get('description')
            inventory.quantity = request.form.get('quantity', type=int)
            inventory.price = request.form.get('price', type=float)
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
            notes=request.form.get('notes')
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
