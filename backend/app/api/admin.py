from flask import Blueprint, request, jsonify
from flask_security import auth_required
from app.models.user import User, Role
from app.models.project import ResearchProject
from app.models.task import Task
from app.models.paper import ResearchPaper
from app.extensions import db, security
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@auth_required('token')
@admin_required
def list_users():
    users = User.query.all()
    return jsonify(message="Users retrieved", data=[u.to_dict() for u in users]), 200

@admin_bp.route('/users/<int:id>', methods=['PUT'])
@auth_required('token')
@admin_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    if 'active' in data:
        user.active = data['active']
    if 'roles' in data:
        user.roles = []
        for r_name in data['roles']:
            r = Role.query.filter_by(name=r_name).first()
            if r:
                user.roles.append(r)
    db.session.commit()
    return jsonify(message="User updated", data=user.to_dict()), 200

@admin_bp.route('/users/<int:id>', methods=['DELETE'])
@auth_required('token')
@admin_required
def deactivate_user(id):
    user = User.query.get_or_404(id)
    user.active = False
    db.session.commit()
    return jsonify(message="User deactivated", data={}), 200

@admin_bp.route('/stats', methods=['GET'])
@auth_required('token')
@admin_required
def stats():
    return jsonify(message="Stats retrieved", data={
        "total_users": User.query.count(),
        "total_projects": ResearchProject.query.count(),
        "total_tasks": Task.query.count(),
        "total_papers": ResearchPaper.query.count()
    }), 200
