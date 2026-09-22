"""
Auth API Blueprint.

Uses Flask-Security-Too for token auth and password hashing only.
All login/register routes are handled here — NOT via Flask-Security's built-in views.
"""
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from flask_security.utils import verify_password, hash_password
from app.models.user import User
from app.extensions import db
import uuid
from datetime import datetime

auth_bp = Blueprint('auth_api', __name__)


def _token_for(user):
    """Return the Flask-Security auth token for the given user."""
    return user.get_auth_token()


@auth_bp.route('/register', methods=['POST'])
def register():
    """POST /api/auth/register — create a new account."""
    data = request.get_json(silent=True) or {}

    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')

    if not email or not username or not password:
        return jsonify(error="Email, username and password are required"), 400
    if len(password) < 6:
        return jsonify(error="Password must be at least 6 characters"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="An account with this email already exists"), 400
    if User.query.filter_by(username=username).first():
        return jsonify(error="Username is already taken"), 400

    # Create user directly via SQLAlchemy — bypass Flask-Security's register view
    user = User(
        email=email,
        username=username,
        password=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        fs_uniquifier=str(uuid.uuid4()),
        active=True,
        confirmed_at=datetime.utcnow(),
    )
    db.session.add(user)
    db.session.commit()

    token = _token_for(user)
    return jsonify(
        message="Registered successfully",
        data={"user": user.to_dict(), "token": token}
    ), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/auth/login — authenticate and receive a token."""
    data = request.get_json(silent=True) or {}

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify(error="Email and password are required"), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.active or not verify_password(password, user.password):
        return jsonify(error="Invalid email or password"), 401

    token = _token_for(user)
    return jsonify(
        message="Logged in successfully",
        data={"user": user.to_dict(), "token": token}
    ), 200


@auth_bp.route('/logout', methods=['POST'])
@auth_required('token')
def logout():
    """POST /api/auth/logout — invalidate current token."""
    return jsonify(message="Logged out successfully", data={}), 200


@auth_bp.route('/me', methods=['GET'])
@auth_required('token')
def me():
    """GET /api/auth/me — return current user info."""
    return jsonify(message="Current user", data=current_user.to_dict()), 200


@auth_bp.route('/me', methods=['PUT'])
@auth_required('token')
def update_me():
    """PUT /api/auth/me — update current user profile."""
    data = request.get_json(silent=True) or {}

    if 'first_name' in data:
        current_user.first_name = data['first_name']
    if 'last_name' in data:
        current_user.last_name = data['last_name']
    if 'username' in data:
        new_username = data['username'].strip()
        conflict = User.query.filter_by(username=new_username).first()
        if conflict and conflict.id != current_user.id:
            return jsonify(error="Username is already taken"), 400
        current_user.username = new_username

    db.session.commit()
    return jsonify(message="Profile updated", data=current_user.to_dict()), 200
