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
