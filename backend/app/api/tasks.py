from flask import Blueprint, request, jsonify
from flask_security import auth_required
from app.models.task import Task
from app.extensions import db
from app.utils.decorators import project_member_required
from datetime import datetime
from app.sockets import emit_notification
from app.models.notification import Notification, NotificationType

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/projects/<int:project_id>/tasks', methods=['POST'])
@auth_required('token')
@project_member_required
def create_task(project_id):
    data = request.get_json()
    dl = data.get('deadline')
    task = Task(
        project_id=project_id,
        assigned_to=data.get('assigned_to'),
        title=data.get('title'),
        description=data.get('description', ''),
        deadline=datetime.fromisoformat(dl) if dl else None
    )
    if 'priority' in data:
        task.priority = data['priority']
    db.session.add(task)
    db.session.commit()
    
    if task.assigned_to:
        notif = Notification(user_id=task.assigned_to, message=f"Assigned new task: {task.title}", type=NotificationType.TASK_ASSIGNED)
        db.session.add(notif)
        db.session.commit()
        emit_notification(task.assigned_to, notif.to_dict())
        
    return jsonify(message="Task created", data=task.to_dict()), 201

@tasks_bp.route('/projects/<int:project_id>/tasks', methods=['GET'])
@auth_required('token')
@project_member_required
def list_tasks(project_id):
    query = Task.query.filter_by(project_id=project_id)
    if 'status' in request.args:
        query = query.filter_by(status=request.args['status'])
    if 'assigned_to' in request.args:
        query = query.filter_by(assigned_to=request.args['assigned_to'])
    tasks = query.all()
    return jsonify(message="Tasks retrieved", data=[t.to_dict() for t in tasks]), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
@auth_required('token')
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(message="Task details", data=task.to_dict()), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@auth_required('token')
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.assigned_to = data.get('assigned_to', task.assigned_to)
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'deadline' in data:
        task.deadline = datetime.fromisoformat(data['deadline']) if data['deadline'] else None
        
    db.session.commit()
    return jsonify(message="Task updated", data=task.to_dict()), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@auth_required('token')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify(message="Task deleted", data={}), 200
