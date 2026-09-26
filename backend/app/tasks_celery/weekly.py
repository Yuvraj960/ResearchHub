from app.extensions import celery, db, mail
from app.models.project import ResearchProject, ProjectMember
from app.models.task import Task, TaskStatus
from app.models.paper import PaperVersion
from app.models.user import User
from flask_mail import Message
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery.task
def send_weekly_digest():
    """
    Runs every Monday at 9 AM (Celery Beat schedule).
    Sends each member of every active project a weekly research summary email.
    """
    from app.models.project import ProjectStatus

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    next_week = now + timedelta(days=7)

    active_projects = ResearchProject.query.filter_by(status=ProjectStatus.ACTIVE).all()

    for project in active_projects:
        members = ProjectMember.query.filter_by(project_id=project.id).all()
        member_user_ids = [m.user_id for m in members]
        users = User.query.filter(User.id.in_(member_user_ids)).all()

        if not users:
            continue

        # Gather weekly stats
        all_tasks = Task.query.filter_by(project_id=project.id).all()
        completed_this_week = [
            t for t in all_tasks
            if t.status == TaskStatus.COMPLETED
            and t.updated_at and t.updated_at >= week_ago
        ]
        pending_tasks = [t for t in all_tasks if t.status != TaskStatus.COMPLETED]
        upcoming_deadlines = [
            t for t in all_tasks
            if t.deadline and now <= t.deadline <= next_week
            and t.status != TaskStatus.COMPLETED
        ]

        recent_versions = PaperVersion.query.join(
            PaperVersion.paper
        ).filter(
            PaperVersion.created_at >= week_ago
        ).all()

        # Build email body
        completed_lines = "".join(
            f"<li>✅ {t.title}</li>" for t in completed_this_week
        ) or "<li>None this week</li>"

        pending_lines = "".join(
            f"<li>🔲 {t.title} <em>({t.status.value})</em></li>"
            for t in pending_tasks[:10]
        ) or "<li>No pending tasks</li>"

        deadline_lines = "".join(
            f"<li>⏰ {t.title} — due {t.deadline.strftime('%b %d, %Y')}</li>"
            for t in upcoming_deadlines
        ) or "<li>No upcoming deadlines</li>"

        version_lines = "".join(
            f"<li>📄 Version {v.version_number} of <em>{v.paper.title}</em> — {v.change_summary or 'no summary'}</li>"
            for v in recent_versions[:5]
        ) or "<li>No new versions this week</li>"

        total = len(all_tasks)
        done = len([t for t in all_tasks if t.status == TaskStatus.COMPLETED])
        progress = int(done / total * 100) if total > 0 else 0

        html_body = f"""
        <h2>📊 Weekly Research Digest — {project.title}</h2>
        <p>Here's your weekly summary for <strong>{project.title}</strong>.</p>
        <p><strong>Overall Progress:</strong> {progress}% ({done}/{total} tasks completed)</p>

        <h3>✅ Completed This Week</h3>
        <ul>{completed_lines}</ul>

        <h3>🔲 Pending Tasks</h3>
        <ul>{pending_lines}</ul>

        <h3>⏰ Upcoming Deadlines (Next 7 Days)</h3>
        <ul>{deadline_lines}</ul>

        <h3>📄 Recent Paper Versions</h3>
        <ul>{version_lines}</ul>

        <br>
        <p style="color:#888">You are receiving this because you are a member of this ResearchHub project.</p>
        """

        for user in users:
            try:
                msg = Message(
                    subject=f"[ResearchHub] Weekly Digest — {project.title}",
                    recipients=[user.email],
                    html=html_body
                )
                mail.send(msg)
                logger.info(f"Weekly digest sent to {user.email} for project {project.id}")
            except Exception as e:
                logger.warning(f"Failed to send digest to {user.email}: {e}")

    return f"Weekly digest sent for {len(active_projects)} active projects"
