import compat  # noqa: F401 – Python 3.12 pkg_resources shim (must be first)
import eventlet
eventlet.monkey_patch()

import os
from app import create_app
from app.extensions import db, socketio

app = create_app(os.getenv('FLASK_ENV', 'development'))

# Auto-create all database tables on first run (SQLite dev mode)
with app.app_context():
    db.create_all()
    print("✅ Database tables created (if not already existing)")

if __name__ == '__main__':
    print("🚀 Starting ResearchHub backend on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=os.getenv('FLASK_ENV') != 'production')
