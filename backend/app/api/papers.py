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
