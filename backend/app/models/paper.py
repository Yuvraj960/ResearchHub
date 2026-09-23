from app.extensions import db
from datetime import datetime
import enum

class PaperStatus(enum.Enum):
    DRAFT = 'DRAFT'
    REVIEW = 'REVIEW'
    SUBMITTED = 'SUBMITTED'
    PUBLISHED = 'PUBLISHED'

class ResearchPaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.Text)
    status = db.Column(db.Enum(PaperStatus), default=PaperStatus.DRAFT)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    versions = db.relationship('PaperVersion', backref='paper', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "abstract": self.abstract,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class PaperVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('research_paper.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text)
    change_summary = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "version_number": self.version_number,
            "created_by": self.created_by,
            "content": self.content,
            "change_summary": self.change_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
