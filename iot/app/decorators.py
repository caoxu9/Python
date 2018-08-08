from flask import abort
from flask_login import current_user
from app.models import Permission
from functools import wraps


def permission_decorator(permissions):
    def decorator(fun):
        @wraps(fun)
        def dec_fun(*args, **kwargs):
            if not current_user.has_permission(permissions):
                abort(403)
            return fun(*args, **kwargs)

        return dec_fun

    return decorator


def admin_decorator(fun):
    return permission_decorator(Permission.ADMIN)(fun)


def assient_decorator(fun):
    return permission_decorator(Permission.FOLLOW | Permission.WRITE | Permission.COMMENT | Permission.MODE_COMMENT)(
        fun)
