from app.extensions import db
from datetime import datetime
import enum

class ProjectStatus(enum.Enum):
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    ARCHIVED = 'ARCHIVED'

class MemberRole(enum.Enum):
    RESEARCHER = 'RESEARCHER'
    OWNER = 'OWNER'

class ResearchProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    field = db.Column(db.String(255))
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    members = db.relationship('ProjectMember', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "title": self.title,
            "description": self.description,
            "field": self.field,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.Enum(MemberRole), default=MemberRole.RESEARCHER)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='memberships')
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "user": self.user.to_dict() if self.user else None
        }
