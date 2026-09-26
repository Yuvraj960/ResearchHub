from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security
from flask_socketio import SocketIO
from flask_mail import Mail
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
security = Security()
socketio = SocketIO()
mail = Mail()
celery = Celery(__name__)
