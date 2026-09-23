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
