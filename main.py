import time
from uuid import uuid4
from flask import Flask, redirect, render_template, request, session
from flask import request as frequest
from api.oauth.token import ClientToken
from api.oauth.calls import oauth_redirect_url
from app.user import process_registration
from misc import build_base_kwargs
from data_structures.general.character import Character

from routes.user import user_blueprint
from routes.characters import characters_blueprint


app = Flask(
    __name__,
    static_url_path='',
    static_folder='web/static',
    template_folder='web/templates'
)
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(characters_blueprint, url_prefix='/characters')
app.secret_key = 'BAD_SECRET_KEY'

state = uuid4().hex
token = None


@app.route("/")
def index():
    return render_template('base/root.html', **build_base_kwargs())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
