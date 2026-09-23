from .events import *
from app.extensions import socketio

def emit_notification(user_id, notification):
    socketio.emit('new_notification', notification, room=f"user_{user_id}")
