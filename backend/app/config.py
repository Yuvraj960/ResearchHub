import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///researchhub.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security-Too — token-only mode, all built-in views hidden
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
    SECURITY_TOKEN_MAX_AGE = 86400              # 24 hours
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'super-secret-salt')
    SECURITY_REGISTERABLE = False               # handled by our own auth blueprint
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_BLUEPRINT_NAME = '_fst_internal'   # hidden internal name
    SECURITY_URL_PREFIX = '/_fst'              # all FST views at /_fst/...
    SECURITY_LOGIN_URL = '/login'
    SECURITY_LOGOUT_URL = '/logout'
    SECURITY_REGISTER_URL = '/register'
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = False
    SECURITY_CONFIRMABLE = False
    SECURITY_TRACKABLE = False

    # Celery + Redis
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Email (SMTP)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # CORS — all localhost ports allowed in dev; in prod set FRONTEND_URL explicitly
    FRONTEND_URL = os.getenv('FRONTEND_URL', '*')

    WTF_CSRF_ENABLED = False


config = {
    'development': Config,
    'production': Config,
    'default': Config,
}
