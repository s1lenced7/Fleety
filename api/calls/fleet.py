from api.calls.base import SwaggerApiCall
from data_structures.fleet.fleet import Fleet


class FleetFromID(SwaggerApiCall):

    route = 'fleets/{fleet_id}/'
    response_type = Fleet

    @classmethod
    def _get(cls, character_id, token):
        return cls._execute(id=character_id, route_args={'character_id': character_id}, token=token)
