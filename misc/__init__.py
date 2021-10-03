from flask import session

from .session_keys import USER, CSRF_TOKEN

def build_base_kwargs(**kwargs):
    return {
        'user': session.get(USER),
        'csrf_token': session.get(CSRF_TOKEN),
    } | kwargs