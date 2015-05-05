from functools import wraps
from flask import abort
from flask.ext.login import current_user


class role_required:
    """
    Check if user has the required roles
    """
    def __init__(self, student=False, teacher=False, cd=False, admin=False):
        self.student = student
        self.teacher = teacher
        self.cd = cd
        self.admin = admin

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            not_abort = (self.admin and current_user.is_admin())
            not_abort = not_abort or (self.teacher and current_user.is_teacher())
            not_abort = not_abort or (self.cd and current_user.is_chief_department())
            not_abort = not_abort or (self.student and current_user.is_student())
            if not_abort:
                return f(*args, **kwargs)
            else:
                abort(403)

        return decorated_function