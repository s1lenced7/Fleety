import time
from uuid import uuid4
from flask import Flask, redirect, render_template, request
from flask import request as frequest
from api.oauth.token import ClientToken
from api.oauth.calls import oauth_redirect_url


app = Flask(
    __name__,
    static_url_path='',
    static_folder='web/static',
    template_folder='web/templates'
)
app.secret_key = 'BAD_SECRET_KEY'

state = uuid4().hex
token = None

base_kwargs = {
    'paths': {
        'sign_in': '/sign_in',
        'register': '/register',
    },
    'user': {
        'signed_in': False
    }
}


@app.route("/")
def index():
    return render_template('base/root.html', **base_kwargs)


@app.route("/sign_in", methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        return render_template('user/sign-in.html', **base_kwargs)
    elif request.method != 'POST':
        return redirect("/")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('user/register.html', **base_kwargs)
    elif request.method != 'POST':
        return redirect("/")

@app.route("/login")
def login():
    return redirect(oauth_redirect_url())


@app.route('/auth_callback')
def auth_callback():
    code = frequest.args.get('code')
    time.sleep(1)
    c = ClientToken.from_oauth_code(code)
    global token
    token = c

    return "<p>Login Success!</p>"

if __name__ == '__main__':
    # quantum = CharacterFromID.get(1416973491)
    # quantum = CharacterFromID.get(1416973491)
    #
    # d = UniverseItemsFromID.get(1416973491, 95465499, 30000142)
    # d = UniverseItemsFromID.get(1416973491, 95465499, 30000142)
    # token = next(ClientToken.from_db(character_id=quantum.id))
    # c = FleetFromCharacterID.get(quantum.id, token)

    # quantum.write_to_db()
    app.run(host='0.0.0.0', port=8080)
