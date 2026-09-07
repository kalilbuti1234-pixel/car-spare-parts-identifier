"""
تطبيق تحديد قطع غيار السيارات
Car Spare Parts Identifier Application
"""

from app import create_app
from app.database import init_db

if __name__ == '__main__':
    app = create_app()
    
    # إنشاء قاعدة البيانات عند التشغيل الأول
    with app.app_context():
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
