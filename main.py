"""
تطبيق تحديد قطع غيار السيارات
Car Spare Parts Identifier Application
Version: Scenario 1.0
"""

import os
from app import create_app, db
from app.models import User, CarType, SparePart, SearchHistory

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'CarType': CarType, 
            'SparePart': SparePart, 'SearchHistory': SearchHistory}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=os.environ.get('FLASK_ENV') == 'development', 
            host='0.0.0.0', port=port)
