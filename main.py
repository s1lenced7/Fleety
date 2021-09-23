import time
from uuid import uuid4
from flask import Flask, redirect #, session
from flask import request as frequest

from task.test_task import TestTask
from api.mock import MOCK_FLEET_MEMBERSHIP_LOGS
from api.calls.character import CharacterFromID
from api.calls.character import FleetFromCharacterID
from api.calls.solar_system import SolarSystemFromID
from api.calls.universe import UniverseItemsFromID
from database.connection import MySQLConnectionManager
from data_structures.app.user import User
from api.oauth.token import ClientToken
from api.oauth.calls import oauth_redirect_url


app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

state = uuid4().hex
token = None

@app.route("/")
def hello_world():
    # t = TestTask(execution_interval=5)
    # t.start()
    return "<p>Hello, World!</p>"


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
    quantum = CharacterFromID.get(1416973491)
    quantum = CharacterFromID.get(1416973491)

    d = UniverseItemsFromID.get(1416973491, 95465499, 30000142)
    d = UniverseItemsFromID.get(1416973491, 95465499, 30000142)
    # token = next(ClientToken.from_db(character_id=quantum.id))
    # c = FleetFromCharacterID.get(quantum.id, token)

    # quantum.write_to_db()
    t = 5
    app.run(host='0.0.0.0', port=8080)
