from app.extensions import db
from datetime import datetime

class Reference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255))
    year = db.Column(db.Integer)
    journal = db.Column(db.String(255))
    doi = db.Column(db.String(255))
    url = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "added_by": self.added_by,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "journal": self.journal,
            "doi": self.doi,
            "url": self.url,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
