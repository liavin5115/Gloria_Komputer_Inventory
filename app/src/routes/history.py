from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_login import login_required, current_user
from app.src.models.inventory import Inventory
from app.src.models.stock_history import StockHistory
from app.src import db, utc_to_local, get_jakarta_time
from datetime import datetime, timedelta
from sqlalchemy import func
import pytz
import io
import csv

history = Blueprint('history', __name__)

@history.route('/history')
@login_required
def history_list():
    try:
        # Get filter parameters
        product_id = request.args.get('product', type=int)
        movement_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Base query
        query = StockHistory.query    

        # Apply filters
        if product_id:
            query = query.filter(StockHistory.inventory_id == product_id)
        if movement_type:
            query = query.filter(StockHistory.type == movement_type)
        if start_date:
            jakarta_tz = pytz.timezone('Asia/Jakarta')
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_dt = jakarta_tz.localize(start_dt)
            query = query.filter(StockHistory.date >= start_dt)
        if end_date:
            jakarta_tz = pytz.timezone('Asia/Jakarta')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_dt = jakarta_tz.localize(end_dt)
            end_dt = end_dt + timedelta(days=1)
            query = query.filter(StockHistory.date < end_dt)

        # Get results
        histories = query.order_by(StockHistory.date.desc()).all()

        # Calculate summaries
        total_in = sum(h.quantity for h in histories if h.type == 'in')
        total_out = sum(h.quantity for h in histories if h.type == 'out')
        total_movements = len(histories)

        # Get all inventory items for the filter dropdown
        inventory_items = Inventory.query.order_by(Inventory.product_name).all()

        return render_template('history/list.html',
                         histories=histories,
                         products=inventory_items,
                         inventory_items=inventory_items,
                         total_in=total_in,
                         total_out=total_out,
                         total_movements=total_movements)
    except Exception as e:
        db.session.rollback()
        flash(f'Error loading history: {str(e)}', 'danger')
        return render_template('history/list.html',
                         histories=[],
                         products=[],
                         inventory_items=[],
                         total_in=0,
                         total_out=0,
                         total_movements=0)

@history.route('/history/add', methods=['GET', 'POST'])
@login_required
def add_history():
    if request.method == 'POST':
        data = request.get_json()
        inventory_id = data.get('inventory_id')
        type = data.get('type')
        quantity = data.get('quantity')
        notes = data.get('notes')
        unit_price = data.get('unit_price')

        if not all([inventory_id, type, quantity, unit_price]):
            return jsonify({'success': False, 'message': 'Data tidak lengkap'})

        try:
            inventory = Inventory.query.get_or_404(inventory_id)
            
            # Validate stock for outgoing movement
            if type == 'out' and quantity > inventory.quantity:
                return jsonify({'success': False, 'message': 'Stock tidak mencukupi'})
            
            # Record stock before movement
            stock_before = inventory.quantity
            
            # Update inventory quantity
            if type == 'in':
                inventory.quantity += quantity
            else:
                inventory.quantity -= quantity
            
            # Create stock history record
            history = StockHistory(
                inventory_id=inventory_id,
                type=type,
                quantity=quantity,
                purchase_price=unit_price if type == 'in' else inventory.purchase_price,
                selling_price=unit_price if type == 'out' else inventory.selling_price,
                notes=notes,
                user_id=current_user.id,
                stock_before=stock_before,
                stock_after=inventory.quantity
            )
            
            # Update inventory prices if it's incoming stock
            if type == 'in':
                inventory.purchase_price = unit_price
            
            db.session.add(history)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Pergerakan stock berhasil dicatat'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

    # GET request untuk form
    inventories = Inventory.query.all()
    return render_template('history/form.html', inventories=inventories)

@history.route('/history/export')
def export_history():
    # Get filter parameters (same as history_list)
    product_id = request.args.get('product', type=int)
    movement_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = StockHistory.query

    # Apply filters with timezone awareness
    if product_id:
        query = query.filter(StockHistory.inventory_id == product_id)
    if movement_type:
        query = query.filter(StockHistory.type == movement_type)
    if start_date:
        jakarta_tz = pytz.timezone('Asia/Jakarta')
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        start_dt = jakarta_tz.localize(start_dt)
        query = query.filter(StockHistory.date >= start_dt)
    if end_date:
        jakarta_tz = pytz.timezone('Asia/Jakarta')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        end_dt = jakarta_tz.localize(end_dt)
        # Add one day to include the entire end date
        end_dt = end_dt + timedelta(days=1)
        query = query.filter(StockHistory.date < end_dt)

    # Get results ordered by date
    histories = query.order_by(StockHistory.date.desc()).all()

    # Create CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header with timezone indicator
    writer.writerow(['Date (WIB)', 'Product', 'Type', 'Quantity', 'Reference', 'Notes'])

    # Write data with localized timestamps
    for history in histories:
        writer.writerow([
            utc_to_local(history.date).strftime('%Y-%m-%d %H:%M:%S'),
            history.inventory.product_name,
            'Stock In' if history.type == 'in' else 'Stock Out',
            history.quantity,
            history.reference,
            history.notes
        ])

    # Prepare response
    output.seek(0)
    current_time = get_jakarta_time().strftime('%Y%m%d_%H%M%S')
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=stock_history_{current_time}_WIB.csv'}
    )

@history.route('/history/<int:id>/detail')
@login_required
def get_history_detail(id):
    try:
        history = StockHistory.query.get_or_404(id)
        return jsonify(history.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def record_stock_history(inventory_id, type, quantity, user_id=None, **kwargs):
    """Helper function to record stock history with before/after quantities"""
    inventory = Inventory.query.get(inventory_id)
    if not inventory:
        raise ValueError("Invalid inventory ID")
        
    stock_before = inventory.quantity
    stock_after = stock_before + quantity if type == 'in' else stock_before - quantity
    
    history = StockHistory(
        inventory_id=inventory_id,
        type=type,
        quantity=quantity,
        user_id=user_id,
        stock_before=stock_before,
        stock_after=stock_after,
        **kwargs
    )
    
    db.session.add(history)
    return history
