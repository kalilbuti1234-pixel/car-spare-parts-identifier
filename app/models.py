"""
نماذج قاعدة البيانات
Database Models
"""

from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """نموذج المستخدم"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    searches = db.relationship('SearchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """تعيين كلمة المرور المشفرة"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class CarType(db.Model):
    """نموذج نوع السيارة"""
    __tablename__ = 'car_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(120), nullable=False)
    year_from = db.Column(db.Integer)
    year_to = db.Column(db.Integer)
    engine_type = db.Column(db.String(120))
    engine_cc = db.Column(db.Integer)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    parts = db.relationship('SparePart', backref='car_type', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CarType {self.brand} {self.model}>'


class SparePart(db.Model):
    """نموذج قطعة الغيار"""
    __tablename__ = 'spare_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    manufacturer = db.Column(db.String(120))
    vin_pattern = db.Column(db.String(255))
    
    # المفتاح الأجنبي
    car_type_id = db.Column(db.Integer, db.ForeignKey('car_types.id'), nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SparePart {self.part_number}>'


class VINDecoder(db.Model):
    """نموذج فك تشفير VIN"""
    __tablename__ = 'vin_decoder'
    
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False, index=True)
    manufacturer = db.Column(db.String(120))
    year = db.Column(db.Integer)
    brand = db.Column(db.String(80))
    model = db.Column(db.String(120))
    engine_type = db.Column(db.String(120))
    body_type = db.Column(db.String(80))
    transmission = db.Column(db.String(80))
    car_type_id = db.Column(db.Integer, db.ForeignKey('car_types.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VINDecoder {self.vin}>'


class SearchHistory(db.Model):
    """نموذج سجل البحث"""
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    vin = db.Column(db.String(17), index=True)
    search_type = db.Column(db.String(50))
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<SearchHistory VIN: {self.vin}>'


class Category(db.Model):
    """نموذج الفئة"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    name_ar = db.Column(db.String(120))
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Category {self.name}>'
