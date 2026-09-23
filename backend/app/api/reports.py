from flask import Blueprint, jsonify, Response
from flask_security import auth_required, current_user
from app.tasks_celery.reports import generate_project_report
from app.utils.decorators import project_member_required
from celery.result import AsyncResult
import base64
import redis
import os

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/', methods=['POST'])
@auth_required('token')
@project_member_required
def generate_report(project_id):
    """Trigger async PDF/text report generation for a project."""
    task = generate_project_report.delay(project_id, current_user.id)
    return jsonify(
        message="Report generation started. You will be notified when ready.",
        data={"task_id": task.id}
    ), 202


@reports_bp.route('/status/<task_id>', methods=['GET'])
@auth_required('token')
@project_member_required
def report_status(project_id, task_id):
    """Poll the status of an async report task."""
    res = AsyncResult(task_id)
    download_url = None
    if res.state == 'SUCCESS':
        download_url = f"/api/projects/{project_id}/report/download/{task_id}"

    return jsonify(message="Report status", data={
        "status": res.state,
        "download_url": download_url
    }), 200


@reports_bp.route('/download/<task_id>', methods=['GET'])
@auth_required('token')
@project_member_required
def download_report(project_id, task_id):
    """Download the generated report content (plain text)."""
    try:
        redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        content_b64 = redis_client.get(f"report_{task_id}")
        if not content_b64:
            return jsonify(error="Report not found or expired", status=404), 404

        content = base64.b64decode(content_b64).decode('utf-8')
        return Response(
            content,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename="project_{project_id}_report.txt"'
            }
        )
    except Exception as e:
        return jsonify(error=f"Failed to retrieve report: {str(e)}", status=500), 500
