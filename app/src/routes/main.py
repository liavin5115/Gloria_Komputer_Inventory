from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app, send_from_directory
from flask_login import login_required, current_user
from app.src.models.inventory import Inventory 
from app.src.models.restock import Restock
from app.src.models.stock_history import StockHistory
from app.src import db, get_jakarta_time
from sqlalchemy import or_, func
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import shutil
import json

main = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join('app', 'src', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
BACKUP_DIR = None  # Will be set in get_backup_dir()
SCHEDULE_FILE = None  # Will be set in get_schedule_file()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_backup_dir():
    global BACKUP_DIR
    if BACKUP_DIR is None:
        app_root = current_app.root_path
        project_root = os.path.abspath(os.path.join(app_root, '..', '..'))
        BACKUP_DIR = os.path.join(project_root, 'backup')
        os.makedirs(BACKUP_DIR, exist_ok=True)
    return BACKUP_DIR

def get_schedule_file():
    global SCHEDULE_FILE
    if SCHEDULE_FILE is None:
        app_root = current_app.root_path
        project_root = os.path.abspath(os.path.join(app_root, '..', '..'))
        SCHEDULE_FILE = os.path.join(project_root, 'backup_schedule.json')
    return SCHEDULE_FILE

def list_backups():
    backup_dir = get_backup_dir()
    backups = []
    for fname in sorted(os.listdir(backup_dir), reverse=True):
        if fname.endswith('.db'):
            fpath = os.path.join(backup_dir, fname)
            stat = os.stat(fpath)
            backups.append({
                'filename': fname,
                'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': f'{stat.st_size // 1024} KB'
            })
    return backups

def get_schedule_time():
    schedule_file = get_schedule_file()
    if os.path.exists(schedule_file):
        with open(schedule_file, 'r') as f:
            data = json.load(f)
            return data.get('time')
    return None

def save_schedule_time(time_str):
    schedule_file = get_schedule_file()
    with open(schedule_file, 'w') as f:
        json.dump({'time': time_str}, f)

@main.route('/')
def landing():
    # Get featured products (those with stock > 0)
    featured_products = Inventory.query.filter(Inventory.quantity > 0).all()
    # Get all products
    all_products = Inventory.query.all()
    # Get unique categories
    categories = db.session.query(Inventory.category).distinct().all()
    categories = [cat[0] for cat in categories]
    # Example testimonials (static, or you can fetch from DB if available)
    testimonials = [
        {"name": "Andi S.", "review": "Great service and fast delivery! My laptop arrived in perfect condition.", "rating": 5},
        {"name": "Maria T.", "review": "Customer support was very helpful. Highly recommended!", "rating": 5},
        {"name": "Budi P.", "review": "Best prices and quality products. Will shop again!", "rating": 4},
    ]
    return render_template(
        'landing.html',
        featured_products=featured_products,
        all_products=all_products,
        categories=categories,
        testimonials=testimonials,
        get_jakarta_time=get_jakarta_time
    )

# --- Route for testing the new landing page design ---
@main.route('/test-landing')
def test_landing_copy():
    """Route to preview the new landing page design with real product data."""
    # Get featured products (e.g. top 3 by quantity or latest)
    featured_products = Inventory.query.order_by(Inventory.quantity.desc()).limit(3).all()
    # Get all products
    all_products = Inventory.query.all()
    # Get unique categories
    categories = db.session.query(Inventory.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    # Example testimonials (static, or you can fetch from DB if available)
    testimonials = [
        {"name": "Andi S.", "review": "Great service and fast delivery! My laptop arrived in perfect condition.", "rating": 5},
        {"name": "Maria T.", "review": "Customer support was very helpful. Highly recommended!", "rating": 5},
        {"name": "Budi P.", "review": "Best prices and quality products. Will shop again!", "rating": 4},
    ]
    return render_template(
        'landing copy.html',
        featured_products=featured_products,
        all_products=all_products,
        categories=categories,
        testimonials=testimonials
    )

@main.route('/inventory/bulk-upload', methods=['POST'])
@login_required
def bulk_upload_inventory():
    if 'photos' not in request.files:
        flash('Tidak ada file yang diupload.', 'danger')
        return redirect(url_for('main.inventory'))
    files = request.files.getlist('photos')
    results = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            product_name = os.path.splitext(filename)[0]
            # Cek duplikasi nama produk
            existing = Inventory.query.filter_by(product_name=product_name).first()
            if existing:
                results.append({'filename': filename, 'status': 'duplicate'})
                continue
            # Hindari tabrakan nama file
            base, ext = os.path.splitext(filename)
            i = 1
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            while os.path.exists(save_path):
                filename = f"{base}_{i}{ext}"
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                i += 1
            try:
                file.save(save_path)
                inventory = Inventory(
                    product_name=product_name,
                    description='',
                    quantity=0,
                    purchase_price=0.0,
                    selling_price=0.0,
                    category='',
                    photo=filename
                )
                db.session.add(inventory)
                db.session.commit()
                results.append({'filename': filename, 'status': 'success'})
            except Exception as e:
                db.session.rollback()
                results.append({'filename': filename, 'status': 'error', 'error': str(e)})
        else:
            results.append({'filename': file.filename, 'status': 'invalid'})
    # Kirim hasil ke frontend (flash message)
    success = [r['filename'] for r in results if r['status'] == 'success']
    duplicate = [r['filename'] for r in results if r['status'] == 'duplicate']
    invalid = [r['filename'] for r in results if r['status'] == 'invalid']
    error = [r for r in results if r['status'] == 'error']
    if success:
        flash(f"Berhasil upload & buat produk: {', '.join(success)}", 'success')
    if duplicate:
        flash(f"Duplikat nama produk (tidak ditambah): {', '.join(duplicate)}", 'warning')
    if invalid:
        flash(f"File tidak valid: {', '.join(invalid)}", 'danger')
    if error:
        flash(f"Gagal upload: {', '.join([e['filename']+': '+e['error'] for e in error])}", 'danger')
    return redirect(url_for('main.inventory'))

@main.route('/dashboard')
@login_required
def index():
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
        func.date(StockHistory.date) == today
    ).scalar() or 0
    
    # Monthly sales
    monthly_sales = db.session.query(
        func.sum(StockHistory.quantity * StockHistory.selling_price)
    ).filter(
        StockHistory.type == 'out',
        func.date(StockHistory.date) >= month_start
    ).scalar() or 0
    
    # Get products with low stock for warning display
    low_stock_items = Inventory.query.filter(Inventory.quantity < 5).all()
    
    # Get recent activities
    recent_activities = StockHistory.query.order_by(StockHistory.date.desc()).limit(5).all()
    
    return render_template('index.html',
                         total_products=total_products,
                         low_stock=low_stock,
                         categories=categories,
                         pending_restocks=pending_restocks,
                         low_stock_items=low_stock_items,
                         total_inventory_value=total_inventory_value,
                         daily_sales=daily_sales,
                         monthly_sales=monthly_sales,
                         recent_activities=recent_activities)

@main.route('/inventory')
@login_required
def inventory():
    # Get all distinct categories for the filter dropdown
    categories = db.session.query(Inventory.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]  # Remove any None values
    
    # Get all inventory items
    inventory_items = Inventory.query.all()
    
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

            photo_filename = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Avoid filename collision
                    base, ext = os.path.splitext(filename)
                    i = 1
                    save_path = os.path.join(UPLOAD_FOLDER, filename)
                    while os.path.exists(save_path):
                        filename = f"{base}_{i}{ext}"
                        save_path = os.path.join(UPLOAD_FOLDER, filename)
                        i += 1
                    file.save(save_path)
                    photo_filename = filename

            inventory = Inventory(
                product_name=request.form.get('product_name'),
                description=request.form.get('description'),
                quantity=request.form.get('quantity', type=int),
                purchase_price=purchase_price,
                selling_price=selling_price,
                category=request.form.get('category'),
                photo=photo_filename
            )
            db.session.add(inventory)
            db.session.commit()
            flash('Produk berhasil ditambahkan', 'success')
            return redirect(url_for('main.inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('main.add_inventory'))
    # Get existing products for the dropdown
    existing_products = Inventory.query.order_by(Inventory.product_name).all()
    return render_template('inventory/form.html', existing_products=existing_products)

@main.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(id):
    inventory = Inventory.query.get_or_404(id)
    if request.method == 'POST':
        try:
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
            # Handle photo update
            if 'photo' in request.files:
                file = request.files['photo']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    base, ext = os.path.splitext(filename)
                    i = 1
                    save_path = os.path.join(UPLOAD_FOLDER, filename)
                    while os.path.exists(save_path):
                        filename = f"{base}_{i}{ext}"
                        save_path = os.path.join(UPLOAD_FOLDER, filename)
                        i += 1
                    file.save(save_path)
                    inventory.photo = filename
            db.session.commit()
            flash('Produk berhasil diperbarui', 'success')
            return redirect(url_for('main.inventory'))
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

@main.route('/inventory/<int:id>/stock-in', methods=['POST'])
@login_required
def stock_in(id):
    try:
        data = request.get_json()
        quantity = int(data.get('quantity', 0))
        
        if not quantity or quantity < 1:
            return jsonify({'error': 'Jumlah tidak valid'}), 400
            
        inventory = Inventory.query.get_or_404(id)
        
        # Record the stock before and calculate stock after
        stock_before = inventory.quantity
        stock_after = stock_before + quantity
        
        # Update inventory
        inventory.quantity = stock_after
        
        # Create stock history with correct stock values
        history = StockHistory(
            inventory_id=id,
            type='in',
            quantity=quantity,
            notes=data.get('notes'),
            reference=data.get('reference'),
            status='completed',
            purchase_price=inventory.purchase_price,
            selling_price=inventory.selling_price,
            stock_before=stock_before,
            stock_after=stock_after,
            user_id=current_user.id if current_user else None
        )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'message': 'Stok berhasil ditambah',
            'new_quantity': inventory.quantity
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main.route('/inventory/<int:id>/stock-out', methods=['POST'])
@login_required
def stock_out(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        quantity = int(data.get('quantity', 0))
        if not quantity or quantity < 1:
            return jsonify({'error': 'Jumlah tidak valid'}), 400
            
        inventory = Inventory.query.get_or_404(id)
        
        if inventory.quantity < quantity:
            return jsonify({'error': 'Stock tidak mencukupi'}), 400
        
        # Record the stock before and calculate stock after
        stock_before = inventory.quantity
        stock_after = stock_before - quantity
        
        # Update inventory
        inventory.quantity = stock_after
        
        # Create stock history
        history = StockHistory(
            inventory_id=id,
            type='out',
            quantity=quantity,
            notes=data.get('notes'),
            reference=data.get('reference'),
            status='completed',
            purchase_price=inventory.purchase_price,
            selling_price=inventory.selling_price,
            stock_before=stock_before,
            stock_after=stock_after,
            user_id=current_user.id if current_user else None
        )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'message': 'Stock berhasil dikurangi',
            'new_quantity': inventory.quantity
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main.route('/products')
def products():
    category = request.args.get('category')
    search = request.args.get('search', '').strip()
    
    query = Inventory.query.filter(Inventory.quantity > 0)
    
    if category:
        query = query.filter(Inventory.category == category)
    if search:
        query = query.filter(
            or_(
                Inventory.product_name.ilike(f'%{search}%'),
                Inventory.description.ilike(f'%{search}%')
            )
        )
    
    products = query.all()
    categories = db.session.query(Inventory.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('products.html',
                         products=products,
                         categories=categories,
                         selected_category=category,
                         search=search)

@main.route('/checkout')
def checkout():
    return render_template('checkout.html')

@main.route('/backup-db')
@login_required
def backup_db():
    import os, shutil
    from flask import flash, redirect
    app_root = current_app.root_path  # This points to app/src
    project_root = os.path.abspath(os.path.join(app_root, '..', '..'))
    db_path = os.path.join(project_root, 'instance', 'inventory.db')
    backup_dir = os.path.join(project_root, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'inventory_backup_{now}.db')
    if not os.path.exists(db_path):
        flash(f'Database file not found at {db_path}', 'danger')
        return redirect(url_for('main.index'))
    try:
        shutil.copy2(db_path, backup_file)
        flash('Database backup created successfully.', 'success')
        return send_file(backup_file, as_attachment=True)
    except Exception as e:
        flash(f'Backup failed: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@main.route('/backup', methods=['GET'])
@login_required
def backup_page():
    backups = list_backups()
    schedule_time = get_schedule_time()
    return render_template('backup.html', backups=backups, schedule_time=schedule_time)

@main.route('/backup/manual', methods=['POST'])
@login_required
def backup_db_manual():
    app_root = current_app.root_path
    project_root = os.path.abspath(os.path.join(app_root, '..', '..'))
    db_path = os.path.join(project_root, 'instance', 'inventory.db')
    backup_dir = get_backup_dir()
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'inventory_backup_{now}.db')
    if not os.path.exists(db_path):
        flash(f'Database file not found at {db_path}', 'danger')
        return redirect(url_for('main.backup_page'))
    try:
        shutil.copy2(db_path, backup_file)
        flash('Database backup created successfully.', 'success')
    except Exception as e:
        flash(f'Backup failed: {str(e)}', 'danger')
    return redirect(url_for('main.backup_page'))

@main.route('/backup/schedule', methods=['POST'])
@login_required
def backup_db_schedule():
    time_str = request.form.get('schedule_time')
    if time_str:
        save_schedule_time(time_str)
        flash('Jadwal backup otomatis disimpan.', 'success')
    else:
        flash('Waktu jadwal tidak valid.', 'danger')
    return redirect(url_for('main.backup_page'))

@main.route('/backup/download/<filename>')
@login_required
def download_backup(filename):
    backup_dir = get_backup_dir()
    return send_from_directory(backup_dir, filename, as_attachment=True)

@main.route('/backup/delete/<filename>')
@login_required
def delete_backup(filename):
    backup_dir = get_backup_dir()
    fpath = os.path.join(backup_dir, filename)
    try:
        if os.path.exists(fpath):
            os.remove(fpath)
            flash('Backup berhasil dihapus.', 'success')
        else:
            flash('File backup tidak ditemukan.', 'danger')
    except Exception as e:
        flash(f'Gagal menghapus backup: {str(e)}', 'danger')
    return redirect(url_for('main.backup_page'))
