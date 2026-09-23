from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.models.project import ProjectMember, MemberRole
from app.models.user import User
from app.extensions import db
from app.utils.decorators import project_owner_required, project_member_required

members_bp = Blueprint('members', __name__)

@members_bp.route('/', methods=['POST'])
@auth_required('token')
@project_owner_required
def add_member(project_id):
    data = request.get_json()
    email = data.get('user_email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(error="User not found", status=404), 404
        
    if ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first():
        return jsonify(error="Already a member", status=400), 400
        
    role = MemberRole(data.get('role', 'RESEARCHER'))
    member = ProjectMember(project_id=project_id, user_id=user.id, role=role)
    db.session.add(member)
    db.session.commit()
    return jsonify(message="Member added", data=member.to_dict()), 201

@members_bp.route('/', methods=['GET'])
@auth_required('token')
@project_member_required
def list_members(project_id):
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    return jsonify(message="Members retrieved", data=[m.to_dict() for m in members]), 200

@members_bp.route('/<int:user_id>', methods=['PUT'])
@auth_required('token')
@project_owner_required
def update_member(project_id, user_id):
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first_or_404()
    data = request.get_json()
    if 'role' in data:
        member.role = MemberRole(data['role'])
    db.session.commit()
    return jsonify(message="Member updated", data=member.to_dict()), 200

@members_bp.route('/<int:user_id>', methods=['DELETE'])
@auth_required('token')
@project_owner_required
def remove_member(project_id, user_id):
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first_or_404()
    db.session.delete(member)
    db.session.commit()
    return jsonify(message="Member removed", data={}), 200
