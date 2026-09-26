from app.extensions import celery, db, mail
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.sockets import emit_notification
from flask_mail import Message
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery.task
def check_deadlines():
    """
    Runs daily (Celery Beat schedule) to find tasks with deadlines within
    the next 48 hours and alert assigned users via notification + email.
    """
    now = datetime.utcnow()
    target = now + timedelta(hours=48)

    tasks = Task.query.filter(
        Task.deadline <= target,
        Task.deadline >= now,
        Task.status != TaskStatus.COMPLETED
    ).all()

    for task in tasks:
        if not task.assigned_to:
            continue

        user = User.query.get(task.assigned_to)
        if not user:
            continue

        hours_left = int((task.deadline - now).total_seconds() / 3600)

        # Create in-app notification
        notif = Notification(
            user_id=user.id,
            message=f"Task '{task.title}' is due in ~{hours_left} hours",
            type=NotificationType.DEADLINE,
            link=f"/projects/{task.project_id}/tasks"
        )
        db.session.add(notif)
        db.session.flush()  # get notif.id before commit

        # Emit real-time WebSocket event
        try:
            emit_notification(user.id, notif.to_dict())
        except Exception as e:
            logger.warning(f"Socket emit failed for user {user.id}: {e}")

        # Send email via Flask-Mail
        try:
            deadline_str = task.deadline.strftime("%B %d, %Y at %H:%M UTC")
            msg = Message(
                subject=f"[ResearchHub] Deadline Reminder: {task.title}",
                recipients=[user.email],
                html=f"""
                <h2>Deadline Reminder</h2>
                <p>Hi {user.first_name or user.username},</p>
                <p>This is a reminder that your task <strong>"{task.title}"</strong>
                   is due on <strong>{deadline_str}</strong> (~{hours_left} hours from now).</p>
                <p>Current status: <strong>{task.status.value}</strong></p>
                <p>Priority: <strong>{task.priority.value}</strong></p>
                <br>
                <p>Log in to ResearchHub to update your task progress.</p>
                """
            )
            mail.send(msg)
        except Exception as e:
            logger.warning(f"Email send failed for user {user.email}: {e}")

    db.session.commit()
    return f"Checked {len(tasks)} upcoming deadline tasks"
