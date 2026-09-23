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
