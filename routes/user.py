from uuid import uuid4
from misc import build_base_kwargs
from misc.session_keys import USER, CSRF_TOKEN
from app.user import process_login, process_registration
from flask import Blueprint, request, session, render_template, redirect

user_blueprint = Blueprint('user', __name__, )


# TODO, protect this endpoint
@user_blueprint.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('user/register.html', **build_base_kwargs())
    elif request.method != 'POST':
        return redirect("/")

    error = ''
    try:
        session[USER] = process_registration().serialize()
        session[CSRF_TOKEN] = uuid4().hex
        return redirect("/")
    except Exception as ex:
        error = str(ex)
    return redirect('')


# TODO, protect this endpoint
@user_blueprint.route('/sign_in', methods=['GET', 'POST'])
def sign_in():

    if request.method == 'GET':
        return render_template('user/sign-in.html', **build_base_kwargs())
    elif request.method != 'POST':
        return redirect("/")

    try:
        session[USER] = process_login().serialize()
        session[CSRF_TOKEN] = uuid4().hex
    except Exception:
        return redirect('')
    return redirect("/")


@user_blueprint.route("/sign_out")
def sign_out():
    # TODO: This is some basic CSRF protection, implement this app wide!
    csrf_token = request.args.get('csrf_token')
    if csrf_token and session.get(CSRF_TOKEN, '') == csrf_token:
        session.clear()
    return redirect("/")


