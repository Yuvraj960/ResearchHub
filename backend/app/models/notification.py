from app.extensions import db
from datetime import datetime
import enum

class NotificationType(enum.Enum):
    DEADLINE = 'DEADLINE'
    TASK_ASSIGNED = 'TASK_ASSIGNED'
    COMMENT = 'COMMENT'
    PAPER_VERSION = 'PAPER_VERSION'
    SYSTEM = 'SYSTEM'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(NotificationType), default=NotificationType.SYSTEM)
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "type": self.type.value,
            "is_read": self.is_read,
            "link": self.link,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
