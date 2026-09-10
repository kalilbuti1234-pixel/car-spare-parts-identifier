"""
مسارات لوحة التحكم (Admin)
Admin Dashboard Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, SparePart, CarType, SearchHistory, VINDecoder, Category
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """ديكوريتور للتحقق من صلاحيات المسؤول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('لا توجد صلاحيات كافية للوصول لهذه الصفحة', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    total_parts = SparePart.query.count()
    total_cars = CarType.query.count()
    total_users = User.query.count()
    total_searches = SearchHistory.query.count()
    
    recent_searches = SearchHistory.query.order_by(
        SearchHistory.created_at.desc()
    ).limit(10).all()
    
    today = datetime.utcnow().date()
    today_searches = SearchHistory.query.filter(
        func.date(SearchHistory.created_at) == today
    ).count()
    
    stats = {
        'total_parts': total_parts,
        'total_cars': total_cars,
        'total_users': total_users,
        'total_searches': total_searches,
        'today_searches': today_searches
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_searches=recent_searches)

# ====== إدارة قطع الغيار ======

@admin_bp.route('/spare-parts')
@login_required
@admin_required
def spare_parts_list():
    """قائمة قطع الغيار"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '').strip()
    
    query = SparePart.query
    if category:
        query = query.filter_by(category=category)
    
    parts = query.paginate(page=page, per_page=20)
    categories = db.session.query(SparePart.category).distinct().all()
    
    return render_template('admin/spare_parts/list.html',
                         parts=parts,
                         categories=categories,
                         selected_category=category)

@admin_bp.route('/spare-parts/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_spare_part():
    """إنشاء قطعة غيار جديدة"""
    if request.method == 'POST':
        try:
            part = SparePart(
                part_number=request.form.get('part_number'),
                name=request.form.get('name'),
                category=request.form.get('category'),
                description=request.form.get('description'),
                price=float(request.form.get('price', 0)),
                stock=int(request.form.get('stock', 0)),
                image_url=request.form.get('image_url'),
                manufacturer=request.form.get('manufacturer'),
                vin_pattern=request.form.get('vin_pattern'),
                car_type_id=int(request.form.get('car_type_id'))
            )
            db.session.add(part)
            db.session.commit()
            flash('تم إنشاء قطعة الغيار بنجاح', 'success')
            return redirect(url_for('admin.spare_parts_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    car_types = CarType.query.all()
    return render_template('admin/spare_parts/create.html', car_types=car_types)

@admin_bp.route('/spare-parts/<int:part_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_spare_part(part_id):
    """تعديل قطعة غيار"""
    part = SparePart.query.get_or_404(part_id)
    
    if request.method == 'POST':
        try:
            part.part_number = request.form.get('part_number')
            part.name = request.form.get('name')
            part.category = request.form.get('category')
            part.description = request.form.get('description')
            part.price = float(request.form.get('price', 0))
            part.stock = int(request.form.get('stock', 0))
            part.image_url = request.form.get('image_url')
            part.manufacturer = request.form.get('manufacturer')
            part.vin_pattern = request.form.get('vin_pattern')
            part.car_type_id = int(request.form.get('car_type_id'))
            part.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('تم تحديث قطعة الغيار بنجاح', 'success')
            return redirect(url_for('admin.spare_parts_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    car_types = CarType.query.all()
    return render_template('admin/spare_parts/edit.html', part=part, car_types=car_types)

@admin_bp.route('/spare-parts/<int:part_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_spare_part(part_id):
    """حذف قطعة غيار"""
    part = SparePart.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    flash('تم حذف قطعة الغيار بنجاح', 'success')
    return redirect(url_for('admin.spare_parts_list'))

# ====== إدارة أنواع السيارات ======

@admin_bp.route('/car-types')
@login_required
@admin_required
def car_types_list():
    """قائمة أنواع السيارات"""
    page = request.args.get('page', 1, type=int)
    brand = request.args.get('brand', '').strip()
    
    query = CarType.query
    if brand:
        query = query.filter_by(brand=brand)
    
    cars = query.paginate(page=page, per_page=20)
    brands = db.session.query(CarType.brand).distinct().all()
    
    return render_template('admin/car_types/list.html',
                         cars=cars,
                         brands=brands,
                         selected_brand=brand)

@admin_bp.route('/car-types/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_car_type():
    """إنشاء نوع سيارة جديد"""
    if request.method == 'POST':
        try:
            car = CarType(
                name=request.form.get('name'),
                brand=request.form.get('brand'),
                model=request.form.get('model'),
                year_from=int(request.form.get('year_from', 0)),
                year_to=int(request.form.get('year_to', 0)),
                engine_type=request.form.get('engine_type'),
                engine_cc=int(request.form.get('engine_cc', 0)),
                description=request.form.get('description')
            )
            db.session.add(car)
            db.session.commit()
            flash('تم إنشاء نوع السيارة بنجاح', 'success')
            return redirect(url_for('admin.car_types_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return render_template('admin/car_types/create.html')

@admin_bp.route('/car-types/<int:car_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_car_type(car_id):
    """تعديل نوع السيارة"""
    car = CarType.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            car.name = request.form.get('name')
            car.brand = request.form.get('brand')
            car.model = request.form.get('model')
            car.year_from = int(request.form.get('year_from', 0))
            car.year_to = int(request.form.get('year_to', 0))
            car.engine_type = request.form.get('engine_type')
            car.engine_cc = int(request.form.get('engine_cc', 0))
            car.description = request.form.get('description')
            car.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('تم تحديث نوع السيارة بنجاح', 'success')
            return redirect(url_for('admin.car_types_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return render_template('admin/car_types/edit.html', car=car)

@admin_bp.route('/car-types/<int:car_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_car_type(car_id):
    """حذف نوع السيارة"""
    car = CarType.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    flash('تم حذف نوع السيارة بنجاح', 'success')
    return redirect(url_for('admin.car_types_list'))

# ====== إدارة المستخدمين ======

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    """قائمة المستخدمين"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20)
    return render_template('admin/users/list.html', users=users)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """تعديل بيانات المستخدم"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            user.full_name = request.form.get('full_name')
            user.email = request.form.get('email')
            user.is_admin = bool(request.form.get('is_admin'))
            user.is_active = bool(request.form.get('is_active'))
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('تم تحديث بيانات المستخدم بنجاح', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return render_template('admin/users/edit.html', user=user)

# ====== الإحصائيات والتقارير ======

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """صفحة التقارير"""
    search_stats = db.session.query(
        func.date(SearchHistory.created_at).label('date'),
        func.count(SearchHistory.id).label('count')
    ).group_by(func.date(SearchHistory.created_at)).order_by(
        func.date(SearchHistory.created_at).desc()
    ).limit(30).all()
    
    return render_template('admin/reports.html', search_stats=search_stats)
