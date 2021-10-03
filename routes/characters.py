from time import sleep
from misc import build_base_kwargs
from misc.decorators import authorized
from misc.session_keys import USER
from flask import Blueprint, session, render_template, redirect, request
from data_structures.general.character import Character

from api.oauth.calls import oauth_redirect_url, oauth_invalidate_token
from api.oauth.token import ClientToken
from api.calls.character import CharacterFromID

characters_blueprint = Blueprint('characters', __name__, )


@characters_blueprint.route("/")
@authorized()
def index():
    characters = [c.serialize() for c in Character.from_db(user_id=session[USER]['id'])]
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
    character = CharacterFromID.get(character_id)
    if not character:
        return redirect('/characters')

    auth_token = next(ClientToken.from_db(character_id=character_id), None)
    if auth_token:
        oauth_invalidate_token(auth_token.refresh_token)
        auth_token.remove_from_db()

    character.user_id = None
    character.write_to_db()
    return redirect('/characters')


@characters_blueprint.route("/link_callback")
@authorized()
def link_callback():
    # TODO protect against multiple Fleety accounts linking a single character!
    code = request.args.get('code')

    # Give it a minute
    sleep(1)
    # Fetch character and translate token
    auth_token = ClientToken.from_oauth_code(code)
    linked_character = CharacterFromID.get(auth_token.character_id)
    linked_character.user_id = session[USER]['id']

    # Persist everything to DB
    linked_character.write_to_db()
    auth_token.write_to_db()

    return redirect('/characters')

