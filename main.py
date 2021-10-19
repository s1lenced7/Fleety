from uuid import uuid4
from flask import Flask, render_template
from misc import build_base_kwargs

from routes.user import user_blueprint
from routes.characters import characters_blueprint
from routes.fleets import fleets_blueprint

app = Flask(
    __name__,
    static_url_path='',
    static_folder='web/static',
    template_folder='web/templates'
)
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(characters_blueprint, url_prefix='/characters')
app.register_blueprint(fleets_blueprint, url_prefix='/fleets')
app.secret_key = 'BAD_SECRET_KEY'

state = uuid4().hex
token = None


@app.route("/")
def index():
    return render_template('base/root.html', **build_base_kwargs())


if __name__ == '__main__':
    from api.model import Character, User, Session, System, UniverseItem

    # with Session() as session:
    #     r = Character.get_and_add(session, 1416973491)
    #     s = System.get_and_add(session, 30002074)
    #     u = UniverseItem.get_and_add(session, [33700])
    #     session.commit()
    #     t =5

    app.run(host='0.0.0.0', port=8080)
