from misc import build_base_kwargs
from misc.decorators import authorized
from misc.session_keys import USER
from flask import Blueprint, session, render_template, request, redirect
from api import FleetParticipation, Fleet, Character, User, Session
from task import start_fleet_task

fleets_blueprint = Blueprint('fleets', __name__, )


@fleets_blueprint.route('/')
@authorized()
def index():
    with Session(expire_on_commit=False) as db_session:
        fleets = db_session.query(Fleet).filter(Fleet.user_id == session[USER]['id']).all()
    return render_template('fleet/fleets.html', **build_base_kwargs(fleets=[f.serialize() for f in fleets]))


@fleets_blueprint.route('/<fleet_id>')
@authorized()
def overview(fleet_id):
    with Session(expire_on_commit=False) as db_session:
        fleet = db_session.query(Fleet).filter(Fleet.user_id == session[USER]['id'], Fleet.id == fleet_id).one()
        summary = fleet.build_fleet_summary(db_session)
    return render_template('fleet/summary.html', **build_base_kwargs(summary=summary))


@fleets_blueprint.route('/new', methods=['GET', 'POST'])
@authorized()
def new():
    if request.method == 'GET':
        with Session(expire_on_commit=False) as db_session:
            usable_characters =  db_session.query(Character).filter(Character.user_id == session[USER]['id']).all()
        return render_template('fleet/new.html', **build_base_kwargs(characters=[c.serialize() for c in usable_characters]))
    elif request.method != 'POST':
        return redirect("/")

    name = request.form.get('name')
    character_id = request.form.get('character')
    if not character_id or not name:
        return redirect("/")

    with Session(expire_on_commit=False) as db_session:
        character = db_session.query(Character).filter(Character.id == int(character_id), Character.user_id == session[USER]['id']).one()
        start_fleet_task(character.user, character, name=name)
    return redirect("/fleets/")