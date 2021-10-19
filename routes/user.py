from uuid import uuid4
from misc import build_base_kwargs
from misc.session_keys import USER, CSRF_TOKEN
from flask import Blueprint, request, session, render_template, redirect

from sqlalchemy.exc import NoResultFound
from api.model import User, Session
from misc.crypto import get_hashed_password, check_password

user_blueprint = Blueprint('user', __name__, )


# TODO, protect this endpoint
@user_blueprint.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('user/register.html', **build_base_kwargs())
    elif request.method != 'POST':
        return redirect("/")
    # TODO Unique USERS!!!!
    try:
        user_name = request.form.get('username')
        if not user_name:
            raise Exception('User Name invalid')
        email = request.form.get('email')
        if not email:
            raise Exception('email invalid')

        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')
        if password != password_repeat:
            raise Exception("Passwords did not match")

        with Session() as db_session:
            existing_user = None
            try:
                existing_user = db_session.query(User).filter(User.email == email).one()
            except NoResultFound:
                pass
            if existing_user:
                raise Exception('Email is taken')
            new_user = User(name=user_name, email=email, password_hash=get_hashed_password(password))
            db_session.add(new_user)
            db_session.commit()
            session[USER] = new_user.serialize()
        session[CSRF_TOKEN] = uuid4().hex
    except Exception as ex:
        return redirect('')
    return redirect('/')


# TODO, protect this endpoint
@user_blueprint.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        return render_template('user/sign-in.html', **build_base_kwargs())
    elif request.method != 'POST':
        return redirect("/")

    try:
        email = request.form.get('email')
        password = request.form.get('password')

        with Session() as db_session:
            user = None
            try:
                user = db_session.query(User).filter(User.email == email).one()
            except NoResultFound:
                pass
            if not user:
                raise Exception('No Matching user')
            if not check_password(password, user.password_hash):
                raise Exception('Incorrect password')
            session[USER] = user.serialize()
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


