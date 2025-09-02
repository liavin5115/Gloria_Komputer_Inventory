from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.src.models.user import User
from app.src import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Berhasil masuk ke sistem', 'success')
            return redirect(next_page or url_for('main.index'))
        
        flash('Username atau password salah', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Berhasil keluar dari sistem', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Password saat ini salah', 'danger')
                return redirect(url_for('auth.profile'))
            
            try:
                current_user.set_password(new_password)
            except ValueError as e:
                flash(str(e), 'danger')
                return redirect(url_for('auth.profile'))
        
        if name:
            current_user.name = name
        
        db.session.commit()
        flash('Profil berhasil diperbarui', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')

@auth.route('/admin/manage', methods=['GET', 'POST'])
@login_required
def manage_admins():
    """Manage admin accounts (owner only)"""
    if not current_user.role == 'owner':
        flash('Only the owner can access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            username = request.form.get('username')
            name = request.form.get('name')
            password = request.form.get('password')
            notes = request.form.get('notes')
            
            if User.query.filter_by(username=username).first():
                flash('Username sudah digunakan.', 'danger')
            else:
                try:
                    # First validate password
                    is_valid, error = User.validate_password(password)
                    if not is_valid:
                        flash(error, 'danger')
                        return redirect(url_for('auth.manage_admins'))

                    new_admin = User(
                        username=username,
                        name=name,
                        role='admin',
                        created_by=current_user.id,
                        notes=notes
                    )
                    new_admin.set_password(password)
                    db.session.add(new_admin)
                    db.session.commit()
                    flash(f'Akun admin berhasil dibuat untuk {name}', 'success')
                except ValueError as e:
                    flash(str(e), 'danger')
                    return redirect(url_for('auth.manage_admins'))
        
        elif action == 'delete':
            user_id = request.form.get('user_id')
            user = User.query.get_or_404(user_id)
            if user.role == 'owner':
                flash('Cannot delete owner account.', 'danger')
            else:
                db.session.delete(user)
                db.session.commit()
                flash(f'Admin account {user.name} has been deleted', 'success')
    
    # Get all admin users
    admins = User.query.filter(User.role != 'user').order_by(User.created_at.desc()).all()
    return render_template('auth/manage_admins.html', admins=admins)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect to login page with a message
    flash('Pendaftaran hanya dapat dilakukan oleh owner/admin', 'warning')
    return redirect(url_for('auth.login'))
