from misc import build_base_kwargs
from misc.decorators import authorized
from misc.session_keys import USER
from flask import Blueprint, session, render_template
from api import Fleet#, ParticipationSummary

fleets_blueprint = Blueprint('fleets', __name__, )


@fleets_blueprint.route("/")
@authorized()
def index():
    fleets = [f.serialize() for f in Fleet.from_db(user_id=session[USER]['id'])]
    return render_template('fleet/fleets.html', **build_base_kwargs(fleets=fleets))


@fleets_blueprint.route("/<fleet_id>")
@authorized()
def overview(fleet_id):
    fleets = [f.serialize() for f in Fleet.from_db(id=fleet_id)]
    participation_summary = ParticipationSummary.from_fleet_id(fleet_id)
    return render_template('fleet/summary.html', **build_base_kwargs(fleet=fleet))

