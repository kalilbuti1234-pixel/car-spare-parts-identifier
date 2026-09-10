"""
تطبيق تحديد قطع غيار السيارات
Car Spare Parts Identifier Application
Version: Scenario 1.0
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """إنشاء وتهيئة تطبيق Flask"""
    app = Flask(__name__)
    
    # إعدادات التطبيق
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///database/parts.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    # تهيئة نظام المصادقة
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول أولاً'
    
    # تسجيل المخططات (Blueprints)
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # إنشاء الجداول
    with app.app_context():
        db.create_all()
    
    return app
