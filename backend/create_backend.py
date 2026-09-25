import os
import base64

base_dir = r"c:\Users\lenovo\Desktop\VS\ResearchHub\backend"

files = {
    "requirements.txt": """
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-Security-Too==5.4.3
Flask-SocketIO==5.3.6
Flask-Mail==0.10.0
Flask-CORS==4.0.1
celery==5.4.0
redis==5.0.7
eventlet==0.36.1
python-dotenv==1.0.1
psycopg2-binary==2.9.9
sqlalchemy==2.0.31
bcrypt==4.1.3
passlib==1.7.4
WTForms==3.1.2
""",
    ".env.example": """
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///researchhub.db
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
FLASK_ENV=development
FRONTEND_URL=http://localhost:5173
""",
    "Dockerfile": """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
""",
    "run.py": """
import eventlet
eventlet.monkey_patch()

from app import create_app
from app.extensions import socketio

app = create_app('development')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
""",
    "celery_worker.py": """
import os
from app import create_app
from app.extensions import celery

app = create_app(os.getenv('FLASK_ENV', 'development'))
app.app_context().push()
""",
    "app/__init__.py": """
from flask import Flask, jsonify
from flask_cors import CORS
import os
from .config import config
from .extensions import db, migrate, security, socketio, mail, celery
from .models.user import User, Role

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    CORS(app, resources={r"/api/*": {"origins": app.config.get('FRONTEND_URL', '*')}}, supports_credentials=True)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from flask_security import SQLAlchemyUserDatastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    
    socketio.init_app(app, cors_allowed_origins='*', async_mode='eventlet')
    mail.init_app(app)
    
    # Configure Celery
    celery.conf.update(app.config)
    
    from app.api.auth import auth_bp
    from app.api.projects import projects_bp
    from app.api.members import members_bp
    from app.api.tasks import tasks_bp
    from app.api.papers import papers_bp
    from app.api.versions import versions_bp
    from app.api.milestones import milestones_bp
    from app.api.references import references_bp
    from app.api.comments import comments_bp
    from app.api.notifications import notifications_bp
    from app.api.reports import reports_bp
    from app.api.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(members_bp, url_prefix='/api/projects/<int:project_id>/members')
    app.register_blueprint(tasks_bp, url_prefix='/api')
    app.register_blueprint(papers_bp, url_prefix='/api')
    app.register_blueprint(versions_bp, url_prefix='/api')
    app.register_blueprint(milestones_bp, url_prefix='/api')
    app.register_blueprint(references_bp, url_prefix='/api')
    app.register_blueprint(comments_bp, url_prefix='/api')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(reports_bp, url_prefix='/api/projects/<int:project_id>/report')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not found", status=404), 404
        
    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="Internal server error", status=500), 500
        
    return app
""",
    "app/config.py": """
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///researchhub.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
    SECURITY_TOKEN_MAX_AGE = 86400  # 24 hours
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'super-secret-salt')
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    WTF_CSRF_ENABLED = False

config = {
    'development': Config,
    'default': Config
}
""",
    "app/extensions.py": """
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security
from flask_socketio import SocketIO
from flask_mail import Mail
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
security = Security()
socketio = SocketIO()
mail = Mail()
celery = Celery(__name__)
""",
    "app/utils/__init__.py": "",
    "app/utils/decorators.py": """
from functools import wraps
from flask import jsonify, request
from flask_security import current_user
from app.models.project import ProjectMember, ResearchProject
from app.models.user import User

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
            
        member = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id, role='OWNER').first()
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
""",
    "app/utils/helpers.py": """
def get_current_user():
    from flask_security import current_user
    return current_user
""",
    "app/models/__init__.py": """
from .user import User, Role
from .project import ResearchProject, ProjectMember
from .paper import ResearchPaper, PaperVersion
from .task import Task
from .milestone import Milestone
from .reference import Reference
from .comment import Comment
from .notification import Notification
""",
    "app/models/user.py": """
from app.extensions import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "active": self.active,
            "roles": [r.name for r in self.roles],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
""",
    "app/models/project.py": """
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
""",
    "app/models/paper.py": """
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
""",
    "app/models/task.py": """
from app.extensions import db
from datetime import datetime
import enum

class TaskPriority(enum.Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'

class TaskStatus(enum.Enum):
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    REVIEW = 'REVIEW'
    COMPLETED = 'COMPLETED'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM)
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "assigned_to": self.assigned_to,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
""",
    "app/models/milestone.py": """
from app.extensions import db
from datetime import datetime
import enum

class MilestoneStatus(enum.Enum):
    PENDING = 'PENDING'
    ACHIEVED = 'ACHIEVED'

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_project.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(MilestoneStatus), default=MilestoneStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
""",
    "app/models/reference.py": """
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
""",
    "app/models/comment.py": """
from app.extensions import db
from datetime import datetime

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('research_paper.id'), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "task_id": self.task_id,
            "paper_id": self.paper_id
        }
""",
    "app/models/notification.py": """
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
""",
    "app/api/__init__.py": "",
    "app/api/auth.py": """
from flask import Blueprint, request, jsonify
from flask_security import verify_password, hash_password, auth_required, current_user
from app.models.user import User
from app.extensions import db, security
import uuid
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    
    if not email or not username or not password:
        return jsonify(error="Email, username and password required", status=400), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already exists", status=400), 400
        
    user_datastore = security.datastore
    user = user_datastore.create_user(
        email=email,
        username=username,
        password=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        fs_uniquifier=str(uuid.uuid4()),
        active=True,
        confirmed_at=datetime.utcnow()
    )
    db.session.commit()
    token = user.get_auth_token()
    return jsonify(message="Registered successfully", data={"user": user.to_dict(), "token": token}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and verify_password(password, user.password):
        token = user.get_auth_token()
        return jsonify(message="Logged in", data={"user": user.to_dict(), "token": token}), 200
        
    return jsonify(error="Invalid credentials", status=401), 401

@auth_bp.route('/logout', methods=['POST'])
@auth_required('token')
def logout():
    # Flask-Security tokens are stateless by default, 
    # a real implementation would use blocklisting.
    return jsonify(message="Logged out successfully", data={}), 200

@auth_bp.route('/me', methods=['GET'])
@auth_required('token')
def me():
    return jsonify(message="Current user", data=current_user.to_dict()), 200

@auth_bp.route('/me', methods=['PUT'])
@auth_required('token')
def update_me():
    data = request.get_json()
    current_user.first_name = data.get('first_name', current_user.first_name)
    current_user.last_name = data.get('last_name', current_user.last_name)
    db.session.commit()
    return jsonify(message="Profile updated", data=current_user.to_dict()), 200
""",
    "app/api/projects.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.models.project import ResearchProject, ProjectMember, MemberRole
from app.models.task import Task
from app.models.paper import ResearchPaper
from app.extensions import db
from app.utils.decorators import project_owner_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/', methods=['POST'])
@auth_required('token')
def create_project():
    data = request.get_json()
    project = ResearchProject(
        owner_id=current_user.id,
        title=data.get('title'),
        description=data.get('description', ''),
        field=data.get('field', '')
    )
    db.session.add(project)
    db.session.flush()
    
    member = ProjectMember(project_id=project.id, user_id=current_user.id, role=MemberRole.OWNER)
    db.session.add(member)
    db.session.commit()
    
    return jsonify(message="Project created", data=project.to_dict()), 201

@projects_bp.route('/', methods=['GET'])
@auth_required('token')
def list_projects():
    memberships = ProjectMember.query.filter_by(user_id=current_user.id).all()
    project_ids = [m.project_id for m in memberships]
    projects = ResearchProject.query.filter(ResearchProject.id.in_(project_ids)).all()
    return jsonify(message="Projects retrieved", data=[p.to_dict() for p in projects]), 200

@projects_bp.route('/<int:project_id>', methods=['GET'])
@auth_required('token')
def get_project(project_id):
    project = ResearchProject.query.get_or_404(project_id)
    # verify membership
    if not ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first():
        return jsonify(error="Forbidden", status=403), 403
        
    tasks = Task.query.filter_by(project_id=project_id).all()
    papers = ResearchPaper.query.filter_by(project_id=project_id).count()
    members = ProjectMember.query.filter_by(project_id=project_id).count()
    
    completed = len([t for t in tasks if t.status.value == 'COMPLETED'])
    total_tasks = len(tasks)
    progress = (completed / total_tasks * 100) if total_tasks > 0 else 0
    
    res = project.to_dict()
    res['stats'] = {
        'task_count': total_tasks,
        'member_count': members,
        'paper_count': papers,
        'progress': progress
    }
    return jsonify(message="Project details", data=res), 200

@projects_bp.route('/<int:project_id>', methods=['PUT'])
@auth_required('token')
@project_owner_required
def update_project(project_id):
    project = ResearchProject.query.get_or_404(project_id)
    data = request.get_json()
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.field = data.get('field', project.field)
    if 'status' in data:
        project.status = data['status']
    db.session.commit()
    return jsonify(message="Project updated", data=project.to_dict()), 200

@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@auth_required('token')
@project_owner_required
def delete_project(project_id):
    project = ResearchProject.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify(message="Project deleted", data={}), 200
""",
    "app/api/members.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.models.project import ProjectMember, MemberRole
from app.models.user import User
from app.extensions import db
from app.utils.decorators import project_owner_required, project_member_required

members_bp = Blueprint('members', __name__)

@members_bp.route('/', methods=['POST'])
@auth_required('token')
@project_owner_required
def add_member(project_id):
    data = request.get_json()
    email = data.get('user_email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(error="User not found", status=404), 404
        
    if ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first():
        return jsonify(error="Already a member", status=400), 400
        
    role = MemberRole(data.get('role', 'RESEARCHER'))
    member = ProjectMember(project_id=project_id, user_id=user.id, role=role)
    db.session.add(member)
    db.session.commit()
    return jsonify(message="Member added", data=member.to_dict()), 201

@members_bp.route('/', methods=['GET'])
@auth_required('token')
@project_member_required
def list_members(project_id):
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    return jsonify(message="Members retrieved", data=[m.to_dict() for m in members]), 200

@members_bp.route('/<int:user_id>', methods=['PUT'])
@auth_required('token')
@project_owner_required
def update_member(project_id, user_id):
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first_or_404()
    data = request.get_json()
    if 'role' in data:
        member.role = MemberRole(data['role'])
    db.session.commit()
    return jsonify(message="Member updated", data=member.to_dict()), 200

@members_bp.route('/<int:user_id>', methods=['DELETE'])
@auth_required('token')
@project_owner_required
def remove_member(project_id, user_id):
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first_or_404()
    db.session.delete(member)
    db.session.commit()
    return jsonify(message="Member removed", data={}), 200
""",
    "app/api/tasks.py": """
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
""",
    "app/api/papers.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required
from app.models.paper import ResearchPaper
from app.extensions import db
from app.utils.decorators import project_member_required

papers_bp = Blueprint('papers', __name__)

@papers_bp.route('/projects/<int:project_id>/papers', methods=['POST'])
@auth_required('token')
@project_member_required
def create_paper(project_id):
    data = request.get_json()
    paper = ResearchPaper(
        project_id=project_id,
        title=data.get('title'),
        abstract=data.get('abstract', '')
    )
    if 'status' in data:
        paper.status = data['status']
    db.session.add(paper)
    db.session.commit()
    return jsonify(message="Paper created", data=paper.to_dict()), 201

@papers_bp.route('/projects/<int:project_id>/papers', methods=['GET'])
@auth_required('token')
@project_member_required
def list_papers(project_id):
    papers = ResearchPaper.query.filter_by(project_id=project_id).all()
    return jsonify(message="Papers retrieved", data=[p.to_dict() for p in papers]), 200

@papers_bp.route('/papers/<int:paper_id>', methods=['GET'])
@auth_required('token')
def get_paper(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    return jsonify(message="Paper details", data=paper.to_dict()), 200

@papers_bp.route('/papers/<int:paper_id>', methods=['PUT'])
@auth_required('token')
def update_paper(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    data = request.get_json()
    paper.title = data.get('title', paper.title)
    paper.abstract = data.get('abstract', paper.abstract)
    if 'status' in data:
        paper.status = data['status']
    db.session.commit()
    return jsonify(message="Paper updated", data=paper.to_dict()), 200

@papers_bp.route('/papers/<int:paper_id>', methods=['DELETE'])
@auth_required('token')
def delete_paper(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    db.session.delete(paper)
    db.session.commit()
    return jsonify(message="Paper deleted", data={}), 200
""",
    "app/api/versions.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.models.paper import PaperVersion, ResearchPaper
from app.extensions import db
import base64

versions_bp = Blueprint('versions', __name__)

@versions_bp.route('/papers/<int:paper_id>/versions', methods=['POST'])
@auth_required('token')
def create_version(paper_id):
    data = request.get_json()
    paper = ResearchPaper.query.get_or_404(paper_id)
    
    last_v = PaperVersion.query.filter_by(paper_id=paper_id).order_by(PaperVersion.version_number.desc()).first()
    next_v = (last_v.version_number + 1) if last_v else 1
    
    content_encoded = base64.b64encode(data.get('content', '').encode('utf-8')).decode('utf-8')
    
    version = PaperVersion(
        paper_id=paper_id,
        version_number=next_v,
        created_by=current_user.id,
        content=content_encoded,
        change_summary=data.get('change_summary', '')
    )
    db.session.add(version)
    db.session.commit()
    return jsonify(message="Version created", data=version.to_dict()), 201

@versions_bp.route('/papers/<int:paper_id>/versions', methods=['GET'])
@auth_required('token')
def list_versions(paper_id):
    versions = PaperVersion.query.filter_by(paper_id=paper_id).all()
    res = []
    for v in versions:
        v_dict = v.to_dict()
        if v_dict['content']:
            v_dict['content'] = base64.b64decode(v_dict['content']).decode('utf-8')
        res.append(v_dict)
    return jsonify(message="Versions retrieved", data=res), 200

@versions_bp.route('/versions/<int:version_id>', methods=['GET'])
@auth_required('token')
def get_version(version_id):
    v = PaperVersion.query.get_or_404(version_id)
    v_dict = v.to_dict()
    if v_dict['content']:
        v_dict['content'] = base64.b64decode(v_dict['content']).decode('utf-8')
    return jsonify(message="Version details", data=v_dict), 200
""",
    "app/api/milestones.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required
from app.models.milestone import Milestone
from app.extensions import db
from app.utils.decorators import project_member_required
from datetime import datetime

milestones_bp = Blueprint('milestones', __name__)

@milestones_bp.route('/projects/<int:project_id>/milestones', methods=['POST'])
@auth_required('token')
@project_member_required
def create_milestone(project_id):
    data = request.get_json()
    due = data.get('due_date')
    m = Milestone(
        project_id=project_id,
        title=data.get('title'),
        description=data.get('description', ''),
        due_date=datetime.fromisoformat(due) if due else None
    )
    if 'status' in data:
        m.status = data['status']
    db.session.add(m)
    db.session.commit()
    return jsonify(message="Milestone created", data=m.to_dict()), 201

@milestones_bp.route('/projects/<int:project_id>/milestones', methods=['GET'])
@auth_required('token')
@project_member_required
def list_milestones(project_id):
    ms = Milestone.query.filter_by(project_id=project_id).all()
    return jsonify(message="Milestones retrieved", data=[m.to_dict() for m in ms]), 200

@milestones_bp.route('/milestones/<int:id>', methods=['GET'])
@auth_required('token')
def get_milestone(id):
    m = Milestone.query.get_or_404(id)
    return jsonify(message="Milestone detail", data=m.to_dict()), 200

@milestones_bp.route('/milestones/<int:id>', methods=['PUT'])
@auth_required('token')
def update_milestone(id):
    m = Milestone.query.get_or_404(id)
    data = request.get_json()
    m.title = data.get('title', m.title)
    m.description = data.get('description', m.description)
    if 'due_date' in data:
        m.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'status' in data:
        m.status = data['status']
    db.session.commit()
    return jsonify(message="Milestone updated", data=m.to_dict()), 200

@milestones_bp.route('/milestones/<int:id>', methods=['DELETE'])
@auth_required('token')
def delete_milestone(id):
    m = Milestone.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    return jsonify(message="Milestone deleted", data={}), 200
""",
    "app/api/references.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.models.reference import Reference
from app.extensions import db
from app.utils.decorators import project_member_required

references_bp = Blueprint('references', __name__)

@references_bp.route('/projects/<int:project_id>/references', methods=['POST'])
@auth_required('token')
@project_member_required
def create_reference(project_id):
    data = request.get_json()
    ref = Reference(
        project_id=project_id,
        added_by=current_user.id,
        title=data.get('title'),
        authors=data.get('authors'),
        year=data.get('year'),
        journal=data.get('journal'),
        doi=data.get('doi'),
        url=data.get('url'),
        notes=data.get('notes')
    )
    db.session.add(ref)
    db.session.commit()
    return jsonify(message="Reference created", data=ref.to_dict()), 201

@references_bp.route('/projects/<int:project_id>/references', methods=['GET'])
@auth_required('token')
@project_member_required
def list_references(project_id):
    refs = Reference.query.filter_by(project_id=project_id).all()
    return jsonify(message="References retrieved", data=[r.to_dict() for r in refs]), 200

@references_bp.route('/references/<int:id>', methods=['GET'])
@auth_required('token')
def get_reference(id):
    ref = Reference.query.get_or_404(id)
    return jsonify(message="Reference details", data=ref.to_dict()), 200

@references_bp.route('/references/<int:id>', methods=['PUT'])
@auth_required('token')
def update_reference(id):
    ref = Reference.query.get_or_404(id)
    data = request.get_json()
    ref.title = data.get('title', ref.title)
    ref.authors = data.get('authors', ref.authors)
    ref.year = data.get('year', ref.year)
    ref.journal = data.get('journal', ref.journal)
    ref.doi = data.get('doi', ref.doi)
    ref.url = data.get('url', ref.url)
    ref.notes = data.get('notes', ref.notes)
    db.session.commit()
    return jsonify(message="Reference updated", data=ref.to_dict()), 200

@references_bp.route('/references/<int:id>', methods=['DELETE'])
@auth_required('token')
def delete_reference(id):
    ref = Reference.query.get_or_404(id)
    db.session.delete(ref)
    db.session.commit()
    return jsonify(message="Reference deleted", data={}), 200
""",
    "app/api/comments.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.models.comment import Comment
from app.extensions import db

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/tasks/<int:id>/comments', methods=['POST'])
@auth_required('token')
def create_task_comment(id):
    data = request.get_json()
    c = Comment(author_id=current_user.id, content=data.get('content'), task_id=id)
    db.session.add(c)
    db.session.commit()
    return jsonify(message="Comment created", data=c.to_dict()), 201

@comments_bp.route('/tasks/<int:id>/comments', methods=['GET'])
@auth_required('token')
def list_task_comments(id):
    cs = Comment.query.filter_by(task_id=id).all()
    return jsonify(message="Comments retrieved", data=[c.to_dict() for c in cs]), 200

@comments_bp.route('/papers/<int:id>/comments', methods=['POST'])
@auth_required('token')
def create_paper_comment(id):
    data = request.get_json()
    c = Comment(author_id=current_user.id, content=data.get('content'), paper_id=id)
    db.session.add(c)
    db.session.commit()
    return jsonify(message="Comment created", data=c.to_dict()), 201

@comments_bp.route('/papers/<int:id>/comments', methods=['GET'])
@auth_required('token')
def list_paper_comments(id):
    cs = Comment.query.filter_by(paper_id=id).all()
    return jsonify(message="Comments retrieved", data=[c.to_dict() for c in cs]), 200

@comments_bp.route('/comments/<int:id>', methods=['DELETE'])
@auth_required('token')
def delete_comment(id):
    c = Comment.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify(message="Comment deleted", data={}), 200
""",
    "app/api/notifications.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.models.notification import Notification
from app.extensions import db

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@auth_required('token')
def list_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify(message="Notifications retrieved", data={
        "items": [n.to_dict() for n in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page
    }), 200

@notifications_bp.route('/<int:id>/read', methods=['PUT'])
@auth_required('token')
def mark_read(id):
    n = Notification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    n.is_read = True
    db.session.commit()
    return jsonify(message="Notification marked read", data=n.to_dict()), 200

@notifications_bp.route('/read-all', methods=['PUT'])
@auth_required('token')
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify(message="All notifications marked read", data={}), 200

@notifications_bp.route('/unread-count', methods=['GET'])
@auth_required('token')
def unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify(message="Unread count", data={"count": count}), 200
""",
    "app/api/reports.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app.tasks_celery.reports import generate_project_report
from celery.result import AsyncResult

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['POST'])
@auth_required('token')
def generate_report(project_id):
    task = generate_project_report.delay(project_id, current_user.id)
    return jsonify(message="Report generation started", data={"task_id": task.id}), 202

@reports_bp.route('/status/<task_id>', methods=['GET'])
@auth_required('token')
def report_status(project_id, task_id):
    res = AsyncResult(task_id)
    url = f"/api/projects/{project_id}/report/download/{task_id}" if res.state == 'SUCCESS' else None
    return jsonify(message="Report status", data={"status": res.state, "result_url": url}), 200
""",
    "app/api/admin.py": """
from flask import Blueprint, request, jsonify
from flask_security import auth_required
from app.models.user import User, Role
from app.models.project import ResearchProject
from app.models.task import Task
from app.models.paper import ResearchPaper
from app.extensions import db, security
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@auth_required('token')
@admin_required
def list_users():
    users = User.query.all()
    return jsonify(message="Users retrieved", data=[u.to_dict() for u in users]), 200

@admin_bp.route('/users/<int:id>', methods=['PUT'])
@auth_required('token')
@admin_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    if 'active' in data:
        user.active = data['active']
    if 'roles' in data:
        user.roles = []
        for r_name in data['roles']:
            r = Role.query.filter_by(name=r_name).first()
            if r:
                user.roles.append(r)
    db.session.commit()
    return jsonify(message="User updated", data=user.to_dict()), 200

@admin_bp.route('/users/<int:id>', methods=['DELETE'])
@auth_required('token')
@admin_required
def deactivate_user(id):
    user = User.query.get_or_404(id)
    user.active = False
    db.session.commit()
    return jsonify(message="User deactivated", data={}), 200

@admin_bp.route('/stats', methods=['GET'])
@auth_required('token')
@admin_required
def stats():
    return jsonify(message="Stats retrieved", data={
        "total_users": User.query.count(),
        "total_projects": ResearchProject.query.count(),
        "total_tasks": Task.query.count(),
        "total_papers": ResearchPaper.query.count()
    }), 200
""",
    "app/tasks_celery/__init__.py": "",
    "app/tasks_celery/deadline.py": """
from app.extensions import celery, db, mail
from app.models.task import Task
from app.models.notification import Notification, NotificationType
from app.sockets import emit_notification
from flask_mail import Message
from datetime import datetime, timedelta

@celery.task
def check_deadlines():
    target = datetime.utcnow() + timedelta(hours=48)
    tasks = Task.query.filter(Task.deadline <= target, Task.deadline >= datetime.utcnow(), Task.status != 'COMPLETED').all()
    
    for t in tasks:
        if t.assigned_to:
            notif = Notification(user_id=t.assigned_to, message=f"Task {t.title} deadline approaching", type=NotificationType.DEADLINE)
            db.session.add(notif)
            emit_notification(t.assigned_to, notif.to_dict())
            
            # optionally send email
            
    db.session.commit()
""",
    "app/tasks_celery/weekly.py": """
from app.extensions import celery, db, mail
from app.models.project import ResearchProject
from flask_mail import Message

@celery.task
def send_weekly_digest():
    pass # Implementation details
""",
    "app/tasks_celery/reports.py": """
from app.extensions import celery, db
from app.sockets import emit_notification
from app.models.notification import Notification, NotificationType
import base64
import redis
import os

@celery.task(bind=True)
def generate_project_report(self, project_id, user_id):
    report_text = f"Report for project {project_id}..."
    content = base64.b64encode(report_text.encode('utf-8')).decode('utf-8')
    
    redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    redis_client.setex(f"report_{self.request.id}", 86400, content)
    
    notif = Notification(user_id=user_id, message="Project report is ready", type=NotificationType.SYSTEM)
    db.session.add(notif)
    db.session.commit()
    
    emit_notification(user_id, notif.to_dict())
    
    return {"status": "Complete", "task_id": self.request.id}
""",
    "app/sockets/__init__.py": """
from .events import *
from app.extensions import socketio

def emit_notification(user_id, notification):
    socketio.emit('new_notification', notification, room=f"user_{user_id}")
""",
    "app/sockets/events.py": """
from app.extensions import socketio
from flask_socketio import join_room, leave_room
from flask import request

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('disconnect')
def handle_disconnect():
    pass

@socketio.on('join_user_room')
def handle_join(data):
    user_id = data.get('user_id')
    if user_id:
        join_room(f"user_{user_id}")
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n")
print("All files generated successfully.")
