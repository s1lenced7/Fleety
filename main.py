import time
from uuid import uuid4
from flask import Flask, redirect #, session
from flask import request as frequest

from task.test_task import TestTask
from api.mock import MOCK_FLEET_MEMBERSHIP_LOGS
from api.calls.character import CharacterFromID
from api.calls.solar_system import SolarSystemFromID
from api.calls.universe import UniverseItemsFromID
from database.connection import MySQLConnectionManager
from api.oauth.token import ClientToken
from api.oauth.calls import oauth_redirect_url


app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

state = uuid4().hex
TOKEN = None

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

    from api.calls.character import FleetFromCharacterID
    x = FleetFromCharacterID.get(c.character_id(), c)
    return "<p>Login Success!</p>"

if __name__ == '__main__':


    # a = CharacterFromID.get(1416973491)
    # b = SolarSystemFromID.get(30002768)
    # c = UniverseItemsFromID.get([2998])
    # f = UniverseItemsFromID.get([2998, 3545])
    # d = CharacterFromID.get(1416973491)

    # fleet = Fleet(1231465631)
    # for idx, raw_fleet_log in enumerate(MOCK_FLEET_MEMBERSHIP_LOGS):
    #     print(f"Compiling log {idx + 1}")
    #     new_participations = Participation.from_json_list(raw_fleet_log, fleet.fleet_id)
    #     fleet.update_participations(new_participations)
    #     time.sleep(5)
    from data_structures.database_object import DatabaseObject
    c = ClientToken.from_db(character_id=123)
    t = 5

    app.run(host='0.0.0.0', port=8080)
