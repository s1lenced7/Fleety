from flask import request
from misc.crypto import get_hashed_password, check_password
from api import User


def process_registration():
    user_name = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    password_repeat = request.form.get('password_repeat')

    if password != password_repeat:
        raise Exception("Passwords did not match")
    existing_user = next(User.from_db(email=email), None)
    if existing_user:
        raise Exception("Email address already exists")
    new_user = User(name=user_name,email=email,password_hash=get_hashed_password(password))
    new_user.write_to_db()
    return new_user


def process_login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = next(User.from_db(email=email), None)
    if not user:
        raise Exception('User does not exist')
    if not check_password(password, user.password_hash):
        raise Exception('Incorrect password')
    return user