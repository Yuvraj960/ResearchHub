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
