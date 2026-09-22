from functools import wraps
from flask import jsonify
from flask_security import current_user
from app.models.project import ProjectMember, MemberRole

def project_member_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        project_id = kwargs.get('project_id')
        if not project_id:
            return jsonify(error="Project ID required", status=400), 400

        member = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()
        if not member and not current_user.has_role('admin'):
            return jsonify(error="Forbidden: Not a project member", status=403), 403

        return f(*args, **kwargs)
    return decorated

def project_owner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        project_id = kwargs.get('project_id')
        if not project_id:
            return jsonify(error="Project ID required", status=400), 400

        member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id,
            role=MemberRole.OWNER
        ).first()
        if not member and not current_user.has_role('admin'):
            return jsonify(error="Forbidden: Project owner required", status=403), 403

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.has_role('admin'):
            return jsonify(error="Forbidden: Admin access required", status=403), 403
        return f(*args, **kwargs)
    return decorated
