from api.calls.base import SwaggerApiCall
from data_structures.fleet.fleet import Fleet


class FleetFromID(SwaggerApiCall):
    route = 'fleets/{fleet_id}/'
    response_type = Fleet

    @classmethod
    def _get(cls, fleet_id, token) -> 'Fleet':
        return cls._execute(id=fleet_id, route_args={'fleet_id': fleet_id}, token=token)
