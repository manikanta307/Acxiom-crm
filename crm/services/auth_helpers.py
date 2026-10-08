import re
from functools import wraps
from flask import abort
from flask_login import current_user


PASSWORD_POLICY = {
    'min_length': 8,
}


def validate_password_policy(password: str) -> (bool, str):
    if len(password) < PASSWORD_POLICY['min_length']:
        return False, f"Password must be at least {PASSWORD_POLICY['min_length']} characters"
    if re.search(r'[A-Z]', password) is None:
        return False, 'Password must include at least one uppercase letter'
    if re.search(r'[a-z]', password) is None:
        return False, 'Password must include at least one lowercase letter'
    if re.search(r'[0-9]', password) is None:
        return False, 'Password must include at least one number'
    if re.search(r'[!@#$%^&*()_+\-=[\]{};:\"\\|,.<>/?]', password) is None:
        return False, 'Password must include at least one special character'
    return True, ''


def role_required(role_name: str):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role != role_name and current_user.role != 'Admin':
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator
