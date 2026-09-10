"""
مسارات المصادقة
Authentication Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """تسجيل مستخدم جديد"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        full_name = request.form.get('full_name')
        
        if not username or not email or not password:
            flash('يرجى ملء جميع الحقول المطلوبة', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != password_confirm:
            flash('كلمات المرور غير متطابقة', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون أطول من 6 أحرف', 'danger')
            return redirect(url_for('auth.register'))
        
        try:
            user = User(
                username=username,
                email=email,
                full_name=full_name
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('تم التسجيل بنجاح! يرجى تسجيل الدخول', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('اسم المستخدم أو البريد الإلكتروني موجود بالفعل', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل دخول المستخدم"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('حسابك معطل', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=bool(remember_me))
            next_page = request.args.get('next')
            
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.index'))
        
        flash('اسم المستخدم أو كلمة المرور غير صحيح', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """تسجيل خروج المستخدم"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('main.index'))
