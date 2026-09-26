from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from .config import config
from .extensions import db, migrate, security, socketio, mail, celery
from .models.user import User, Role


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ── CORS ──────────────────────────────────────────────────────────────
    # Allow all origins in development. In production set FRONTEND_URL env var.
    allowed_origins = app.config.get('FRONTEND_URL', '*')
    CORS(app,
         resources={r"/*": {"origins": allowed_origins}},
         supports_credentials=False,      # token auth only — no cookies
         allow_headers=["Content-Type", "Authorization", "Accept"],
         expose_headers=["Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

    # Ensure OPTIONS preflight always gets a 200 with correct CORS headers
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Origin'] = allowed_origins if allowed_origins != '*' else (origin or '*')
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        return response

    # ── Database ──────────────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)

    # ── Flask-Security (token auth only, views hidden at /_fst/*) ─────────
    from flask_security import SQLAlchemyUserDatastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)

    # ── Real-time / Mail / Celery ─────────────────────────────────────────
    socketio.init_app(app, cors_allowed_origins='*', async_mode='eventlet')
    mail.init_app(app)
    celery.conf.update(app.config)

    # ── Register sockets ─────────────────────────────────────────────────
    from app.sockets import events  # noqa: F401 — registers @socketio.on handlers

    # ── Register API blueprints ───────────────────────────────────────────
    from app.api.auth import auth_bp
    from app.api.projects import projects_bp
    from app.api.members import members_bp
    from app.api.tasks import tasks_bp
    from app.api.papers import papers_bp
    from app.api.versions import versions_bp
    from app.api.milestones import milestones_bp
    from app.api.references import references_bp
    from app.api.comments import comments_bp
    from app.api.notifications import notifications_bp
    from app.api.reports import reports_bp
    from app.api.admin import admin_bp

    # Auth MUST be registered before Flask-Security can intercept
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(members_bp, url_prefix='/api/projects/<int:project_id>/members')
    app.register_blueprint(tasks_bp, url_prefix='/api')
    app.register_blueprint(papers_bp, url_prefix='/api')
    app.register_blueprint(versions_bp, url_prefix='/api')
    app.register_blueprint(milestones_bp, url_prefix='/api')
    app.register_blueprint(references_bp, url_prefix='/api')
    app.register_blueprint(comments_bp, url_prefix='/api')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(reports_bp, url_prefix='/api/projects/<int:project_id>/report')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # ── Global error handlers ─────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="Internal server error"), 500

    return app
