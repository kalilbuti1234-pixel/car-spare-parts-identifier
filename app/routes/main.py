"""
المسارات الرئيسية
Main Routes
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import SparePart, CarType, SearchHistory, Category
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """الصفحة الرئيسية"""
    categories = Category.query.all()
    car_types = CarType.query.limit(6).all()
    return render_template('index.html', categories=categories, car_types=car_types)

@main_bp.route('/search')
def search():
    """البحث عن قطع الغيار"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    
    results = []
    total = 0
    
    if query:
        if search_type == 'vin' or search_type == 'all':
            results.extend(
                SparePart.query.filter(
                    SparePart.vin_pattern.ilike(f'%{query}%')
                ).all()
            )
        
        if search_type == 'part_number' or search_type == 'all':
            results.extend(
                SparePart.query.filter(
                    SparePart.part_number.ilike(f'%{query}%')
                ).all()
            )
        
        if search_type == 'name' or search_type == 'all':
            results.extend(
                SparePart.query.filter(
                    SparePart.name.ilike(f'%{query}%')
                ).all()
            )
        
        results = list({r.id: r for r in results}.values())
        total = len(results)
        
        if current_user.is_authenticated:
            search_record = SearchHistory(
                user_id=current_user.id,
                vin=query if search_type == 'vin' else None,
                search_type=search_type,
                results_count=total
            )
            db.session.add(search_record)
            db.session.commit()
    
    return render_template('search.html', 
                         results=results, 
                         query=query, 
                         total=total,
                         search_type=search_type)

@main_bp.route('/parts/<int:part_id>')
def part_detail(part_id):
    """تفاصيل قطعة الغيار"""
    part = SparePart.query.get_or_404(part_id)
    related_parts = SparePart.query.filter(
        SparePart.car_type_id == part.car_type_id,
        SparePart.id != part.id,
        SparePart.category == part.category
    ).limit(4).all()
    
    return render_template('part_detail.html', part=part, related_parts=related_parts)

@main_bp.route('/cars')
def cars():
    """قائمة أنواع السيارات"""
    page = request.args.get('page', 1, type=int)
    brand = request.args.get('brand', '').strip()
    
    query = CarType.query
    if brand:
        query = query.filter_by(brand=brand)
    
    cars = query.paginate(page=page, per_page=12)
    brands = db.session.query(CarType.brand).distinct().all()
    
    return render_template('cars.html', cars=cars, brands=brands, selected_brand=brand)

@main_bp.route('/categories')
def categories():
    """قائمة الفئات"""
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@main_bp.route('/about')
def about():
    """صفحة معلومات التطبيق"""
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """صفحة الاتصال"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        return jsonify({'status': 'success', 'message': 'تم استقبال رسالتك'}), 200
    
    return render_template('contact.html')
