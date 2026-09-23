from flask import Blueprint, request, jsonify
from flask_security import auth_required
from app.models.milestone import Milestone
from app.extensions import db
from app.utils.decorators import project_member_required
from datetime import datetime

milestones_bp = Blueprint('milestones', __name__)

@milestones_bp.route('/projects/<int:project_id>/milestones', methods=['POST'])
@auth_required('token')
@project_member_required
def create_milestone(project_id):
    data = request.get_json()
    due = data.get('due_date')
    m = Milestone(
        project_id=project_id,
        title=data.get('title'),
        description=data.get('description', ''),
        due_date=datetime.fromisoformat(due) if due else None
    )
    if 'status' in data:
        m.status = data['status']
    db.session.add(m)
    db.session.commit()
    return jsonify(message="Milestone created", data=m.to_dict()), 201

@milestones_bp.route('/projects/<int:project_id>/milestones', methods=['GET'])
@auth_required('token')
@project_member_required
def list_milestones(project_id):
    ms = Milestone.query.filter_by(project_id=project_id).all()
    return jsonify(message="Milestones retrieved", data=[m.to_dict() for m in ms]), 200

@milestones_bp.route('/milestones/<int:id>', methods=['GET'])
@auth_required('token')
def get_milestone(id):
    m = Milestone.query.get_or_404(id)
    return jsonify(message="Milestone detail", data=m.to_dict()), 200

@milestones_bp.route('/milestones/<int:id>', methods=['PUT'])
@auth_required('token')
def update_milestone(id):
    m = Milestone.query.get_or_404(id)
    data = request.get_json()
    m.title = data.get('title', m.title)
    m.description = data.get('description', m.description)
    if 'due_date' in data:
        m.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'status' in data:
        m.status = data['status']
    db.session.commit()
    return jsonify(message="Milestone updated", data=m.to_dict()), 200

@milestones_bp.route('/milestones/<int:id>', methods=['DELETE'])
@auth_required('token')
def delete_milestone(id):
    m = Milestone.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    return jsonify(message="Milestone deleted", data={}), 200
