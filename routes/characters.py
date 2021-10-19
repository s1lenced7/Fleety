from time import sleep
from misc import build_base_kwargs
from misc.decorators import authorized
from misc.session_keys import USER
from flask import Blueprint, session, render_template, redirect, request

from api import oauth_redirect_url, oauth_invalidate_token
from api.model import Character, ClientToken, Session, User

characters_blueprint = Blueprint('characters', __name__, )


@characters_blueprint.route("/")
@authorized()
def index():
    serialised_characters = []
    with Session() as db_session:
        characters = db_session.query(Character).filter(Character.user_id == session[USER]['id']).all()
        for character in characters:
            serialised_characters.append(character.serialize())
    return render_template('user/characters.html', **build_base_kwargs(characters=characters))


@characters_blueprint.route("/link")
@authorized()
def link():
    return redirect(oauth_redirect_url())


@characters_blueprint.route("/unlink")
@authorized()
def unlink():
    character_id = request.args.get('character_id')
    if not character_id:
        return redirect('/characters')
    with Session() as db_session:
        character = db_session.query(Character).filter(Character.id == int(character_id), Character.user_id == session[USER]['id']).one()

        client_token = character.client_token
        if client_token:
            oauth_invalidate_token(client_token.refresh_token)
            db_session.delete(client_token)
        character.user_id = None
        db_session.commit()
    return redirect('/characters')


@characters_blueprint.route("/link_callback")
@authorized()
def link_callback():
    # TODO protect against multiple Fleety accounts linking a single character!
    code = request.args.get('code')
    # Give it a minute
    sleep(1)

    # Fetch character and translate token
    client_token = ClientToken.from_oauth_code(code)
    with Session() as db_session:
        character = Character.get_and_add(db_session, client_token.character_id)
        if character.user:
            raise Exception('Character Already linked!')

        # Link character & user
        user = db_session.query(User).filter(User.id == session[USER]['id']).one()
        character.user_id = user.id

        # Link Character & Token
        db_session.add(client_token)
        client_token.character_id = character.id
        db_session.commit()
    return redirect('/characters')

