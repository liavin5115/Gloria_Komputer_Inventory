from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from app.src.models.inventory import Inventory
from app.src.models.stock_history import StockHistory
from app.src import db, utc_to_local, get_jakarta_time
from datetime import datetime, timedelta
from sqlalchemy import func
import pytz
import io
import csv
import csv
import io

history = Blueprint('history', __name__)

@history.route('/history')
def history_list():
    # Get filter parameters
    product_id = request.args.get('product', type=int)
    movement_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = StockHistory.query    # Apply filters
    if product_id:
        query = query.filter(StockHistory.inventory_id == product_id)
    if movement_type:
        query = query.filter(StockHistory.type == movement_type)
    if start_date:
        # Convert start date string to Jakarta timezone datetime
        jakarta_tz = pytz.timezone('Asia/Jakarta')
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        start_dt = jakarta_tz.localize(start_dt)
        query = query.filter(StockHistory.date >= start_dt)
    if end_date:
        # Convert end date string to Jakarta timezone datetime
        jakarta_tz = pytz.timezone('Asia/Jakarta')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        end_dt = jakarta_tz.localize(end_dt)
        # Add one day to include the entire end date
        end_dt = end_dt + timedelta(days=1)
        query = query.filter(StockHistory.date < end_dt)

    # Get results
    histories = query.order_by(StockHistory.date.desc()).all()

    # Calculate summaries
    total_in = sum(h.quantity for h in histories if h.type == 'in')
    total_out = sum(h.quantity for h in histories if h.type == 'out')

    # Get all products for the filter dropdown
    products = Inventory.query.order_by(Inventory.product_name).all()

    return render_template('history/list.html',
                         histories=histories,
                         products=products,
                         total_in=total_in,
                         total_out=total_out)

@history.route('/history/add', methods=['GET', 'POST'])
def add_history():
    if request.method == 'POST':
        inventory_id = int(request.form['inventory_id'])
        quantity = int(request.form['quantity'])
        type = request.form['type']
        
        inventory = Inventory.query.get_or_404(inventory_id)
        
        # Update inventory quantity
        if type == 'in':
            inventory.quantity += quantity
        else:  # type == 'out'
            if inventory.quantity >= quantity:
                inventory.quantity -= quantity
            else:
                flash('Error: Not enough stock available!', 'danger')
                return redirect(url_for('history.add_history'))
        
        # Create history record
        history = StockHistory(
            inventory_id=inventory_id,
            type=type,
            quantity=quantity,
            notes=request.form['notes'],
            reference=request.form['reference']
        )
        
        db.session.add(history)
        db.session.commit()
        
        flash('Stock movement recorded successfully!', 'success')
        return redirect(url_for('history.history_list'))
    
    # Get all inventory items for the form
    inventory_items = Inventory.query.all()
    return render_template('history/form.html', inventory_items=inventory_items)

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
