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

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        
        if not all([username, password, confirm_password]):
            flash('Semua field harus diisi', 'danger')
            return redirect(url_for('auth.register'))
            
        if password != confirm_password:
            flash('Password tidak cocok', 'danger')
            return redirect(url_for('auth.register'))
        
        # First validate password strength
        is_valid, error = User.validate_password(password)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('auth.register'))
            
        user, error = User.register(
            username=username,
            password=password,
            name=name
        )
        
        if error:
            flash(error, 'danger')
            return redirect(url_for('auth.register'))
            
        flash('Registrasi berhasil! Silakan login', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')
