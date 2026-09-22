def get_current_user():
    from flask_security import current_user
    return current_user
