from flask_login import UserMixin
from app.src import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100))
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20), default='user')  # admin or user
    is_active = db.Column(db.Boolean, default=True)
    
    @staticmethod
    def validate_password(password):
        """
        Validates password strength requirements
        Returns (bool, str) - (is_valid, error_message)
        """
        if len(password) < 8:
            return False, 'Password harus minimal 8 karakter'
            
        if not any(c.isupper() for c in password):
            return False, 'Password harus mengandung minimal 1 huruf kapital'
            
        if not any(c.islower() for c in password):
            return False, 'Password harus mengandung minimal 1 huruf kecil'
            
        if not any(c.isdigit() for c in password):
            return False, 'Password harus mengandung minimal 1 angka'
            
        # At least one special character
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(c in special_chars for c in password):
            return False, 'Password harus mengandung minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)'
            
        return True, None
    
    def set_password(self, password):
        is_valid, error = self.validate_password(password)
        if not is_valid:
            raise ValueError(error)
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def register(cls, username, password, name=None, role='user'):
        if cls.query.filter_by(username=username).first():
            return None, 'Username sudah digunakan'
            
        # Validate password strength
        is_valid, error = cls.validate_password(password)
        if not is_valid:
            return None, error
            
        user = cls(
            username=username,
            name=name,
            role=role,
            is_active=True
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f'Terjadi kesalahan saat registrasi: {str(e)}'
    
    def __repr__(self):
        return f'<User {self.username}>'
