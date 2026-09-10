"""
مسارات API
API Routes
"""

from flask import Blueprint, jsonify, request
from app import db
from app.models import SparePart, CarType, VINDecoder

api_bp = Blueprint('api', __name__)

@api_bp.route('/search', methods=['GET'])
def api_search():
    """البحث عن قطع الغيار عبر API"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    
    if not query or len(query) < 2:
        return jsonify({'error': 'البحث يجب أن يكون أطول من حرفين'}), 400
    
    results = []
    
    if search_type in ['vin', 'all']:
        results.extend([
            {'id': p.id, 'part_number': p.part_number, 'name': p.name, 
             'price': p.price, 'stock': p.stock, 'category': p.category}
            for p in SparePart.query.filter(
                SparePart.vin_pattern.ilike(f'%{query}%')
            ).limit(10).all()
        ])
    
    if search_type in ['part_number', 'all']:
        results.extend([
            {'id': p.id, 'part_number': p.part_number, 'name': p.name, 
             'price': p.price, 'stock': p.stock, 'category': p.category}
            for p in SparePart.query.filter(
                SparePart.part_number.ilike(f'%{query}%')
            ).limit(10).all()
        ])
    
    unique_results = {r['id']: r for r in results}
    
    return jsonify({
        'success': True,
        'count': len(unique_results),
        'results': list(unique_results.values())
    }), 200

@api_bp.route('/health', methods=['GET'])
def health_check():
    """فحص صحة API"""
    return jsonify({
        'status': 'ok',
        'message': 'API is running'
    }), 200
