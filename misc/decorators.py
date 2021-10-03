from flask import session, abort
from functools import wraps

from .session_keys import USER


def authorized():
    def authorization_decorator_method(fn):
        @wraps(fn)
        def authorise(*args, **kwargs):
            user = session.get(USER)
            if user:
                return fn(*args, **kwargs)
            return abort(403)
        return authorise
    return authorization_decorator_method