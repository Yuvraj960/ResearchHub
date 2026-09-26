from app.extensions import celery, db, mail
from app.sockets import emit_notification
from app.models.notification import Notification, NotificationType
from flask_mail import Message
import base64
import redis
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@celery.task(bind=True)
def generate_project_report(self, project_id, user_id):
    """
    Triggered on-demand. Builds a plain-text report for the given project,
    stores it base64-encoded in Redis (keyed by Celery task_id), then
    notifies the requesting user via notification + email.
    """
    from app.models.project import ResearchProject
    from app.models.task import Task, TaskStatus
    from app.models.paper import ResearchPaper, PaperVersion
    from app.models.project import ProjectMember
    from app.models.milestone import Milestone, MilestoneStatus
    from app.models.user import User

    project = ResearchProject.query.get(project_id)
    user = User.query.get(user_id)

    if not project or not user:
        return {"status": "error", "message": "Project or user not found"}

    now = datetime.utcnow()
    tasks = Task.query.filter_by(project_id=project_id).all()
    papers = ResearchPaper.query.filter_by(project_id=project_id).all()
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    milestones = Milestone.query.filter_by(project_id=project_id).all()

    completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
    pending = [t for t in tasks if t.status != TaskStatus.COMPLETED]
    overdue = [t for t in pending if t.deadline and t.deadline < now]

    total = len(tasks)
    progress = int(len(completed) / total * 100) if total > 0 else 0

    lines = [
        "=" * 60,
        f"RESEARCH PROJECT REPORT",
        f"Generated: {now.strftime('%B %d, %Y at %H:%M UTC')}",
        "=" * 60,
        "",
        f"Project:     {project.title}",
        f"Field:       {project.field or 'N/A'}",
        f"Status:      {project.status.value}",
        f"Created:     {project.created_at.strftime('%B %d, %Y') if project.created_at else 'N/A'}",
        "",
        f"Description: {project.description or 'N/A'}",
        "",
        "-" * 60,
        "PROGRESS SUMMARY",
        "-" * 60,
        f"Total Tasks:     {total}",
        f"Completed:       {len(completed)}",
        f"Pending:         {len(pending)}",
        f"Overdue:         {len(overdue)}",
        f"Progress:        {progress}%",
        f"Total Papers:    {len(papers)}",
        f"Total Members:   {len(members)}",
        f"Milestones:      {len([m for m in milestones if m.status == MilestoneStatus.ACHIEVED])}/{len(milestones)} achieved",
        "",
        "-" * 60,
        "TASKS",
        "-" * 60,
    ]

    for task in tasks:
        status_icon = "✓" if task.status == TaskStatus.COMPLETED else "○"
        deadline_str = task.deadline.strftime('%Y-%m-%d') if task.deadline else "No deadline"
        lines.append(f"  [{status_icon}] {task.title}")
        lines.append(f"       Status: {task.status.value} | Priority: {task.priority.value} | Deadline: {deadline_str}")

    lines += [
        "",
        "-" * 60,
        "RESEARCH PAPERS",
        "-" * 60,
    ]
    for paper in papers:
        version_count = PaperVersion.query.filter_by(paper_id=paper.id).count()
        lines.append(f"  • {paper.title}")
        lines.append(f"    Status: {paper.status.value} | Versions: {version_count}")

    lines += [
        "",
        "-" * 60,
        "MILESTONES",
        "-" * 60,
    ]
    for ms in milestones:
        icon = "✓" if ms.status == MilestoneStatus.ACHIEVED else "○"
        due = ms.due_date.strftime('%Y-%m-%d') if ms.due_date else "No date"
        lines.append(f"  [{icon}] {ms.title} (due: {due})")

    lines += ["", "=" * 60, "End of Report", "=" * 60]

    report_text = "\n".join(lines)
    content_b64 = base64.b64encode(report_text.encode('utf-8')).decode('utf-8')

    # Store in Redis with 24-hour TTL
    try:
        redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        redis_client.setex(f"report_{self.request.id}", 86400, content_b64)
    except Exception as e:
        logger.warning(f"Redis store failed: {e}")

    # Create in-app notification
    notif = Notification(
        user_id=user_id,
        message=f"Your report for '{project.title}' is ready",
        type=NotificationType.SYSTEM,
        link=f"/api/projects/{project_id}/report/status/{self.request.id}"
    )
    db.session.add(notif)
    db.session.commit()

    # Emit WebSocket
    try:
        emit_notification(user_id, notif.to_dict())
    except Exception as e:
        logger.warning(f"Socket emit failed: {e}")

    # Send email with report as attachment text
    try:
        msg = Message(
            subject=f"[ResearchHub] Report Ready — {project.title}",
            recipients=[user.email],
            html=f"""
            <h2>Your Research Report is Ready</h2>
            <p>Hi {user.first_name or user.username},</p>
            <p>Your report for <strong>{project.title}</strong> has been generated.</p>
            <p>Log in to ResearchHub to download it, or view the summary below:</p>
            <ul>
                <li>Total Tasks: {total} ({len(completed)} completed, {progress}% done)</li>
                <li>Research Papers: {len(papers)}</li>
                <li>Team Members: {len(members)}</li>
                <li>Milestones: {len([m for m in milestones if m.status == MilestoneStatus.ACHIEVED])}/{len(milestones)} achieved</li>
            </ul>
            """,
            body=report_text
        )
        mail.send(msg)
    except Exception as e:
        logger.warning(f"Email send failed: {e}")

    return {"status": "complete", "task_id": self.request.id}
