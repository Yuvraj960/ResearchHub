from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.models.project import ResearchProject, ProjectMember, MemberRole
from app.models.task import Task
from app.models.paper import ResearchPaper
from app.extensions import db
from app.utils.decorators import project_owner_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/', methods=['POST'])
@auth_required('token')
def create_project():
    data = request.get_json()
    project = ResearchProject(
        owner_id=current_user.id,
        title=data.get('title'),
        description=data.get('description', ''),
        field=data.get('field', '')
    )
    db.session.add(project)
    db.session.flush()
    
    member = ProjectMember(project_id=project.id, user_id=current_user.id, role=MemberRole.OWNER)
    db.session.add(member)
    db.session.commit()
    
    return jsonify(message="Project created", data=project.to_dict()), 201

@projects_bp.route('/', methods=['GET'])
@auth_required('token')
def list_projects():
    memberships = ProjectMember.query.filter_by(user_id=current_user.id).all()
    project_ids = [m.project_id for m in memberships]
    projects = ResearchProject.query.filter(ResearchProject.id.in_(project_ids)).all()
    return jsonify(message="Projects retrieved", data=[p.to_dict() for p in projects]), 200

@projects_bp.route('/<int:project_id>', methods=['GET'])
@auth_required('token')
def get_project(project_id):
    project = ResearchProject.query.get_or_404(project_id)
    if not ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first():
        return jsonify(error="Forbidden", status=403), 403
        
    tasks = Task.query.filter_by(project_id=project_id).all()
    papers = ResearchPaper.query.filter_by(project_id=project_id).count()
    members = ProjectMember.query.filter_by(project_id=project_id).count()
    
    completed = len([t for t in tasks if t.status.value == 'COMPLETED'])
    total_tasks = len(tasks)
    progress = (completed / total_tasks * 100) if total_tasks > 0 else 0
    
    res = project.to_dict()
    res['stats'] = {
        'task_count': total_tasks,
        'member_count': members,
        'paper_count': papers,
        'progress': progress
    }
    return jsonify(message="Project details", data=res), 200

@projects_bp.route('/<int:project_id>', methods=['PUT'])
@auth_required('token')
@project_owner_required
def update_project(project_id):
    project = ResearchProject.query.get_or_404(project_id)
    data = request.get_json()
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.field = data.get('field', project.field)
    if 'status' in data:
        project.status = data['status']
    db.session.commit()
    return jsonify(message="Project updated", data=project.to_dict()), 200

@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@auth_required('token')
@project_owner_required
def delete_project(project_id):
    project = ResearchProject.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify(message="Project deleted", data={}), 200
