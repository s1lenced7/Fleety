from api.calls.base import SwaggerApiCall
from data_structures.fleet.participation import Participation


class ParticipationsFromFleetID(SwaggerApiCall):
    route = 'fleets/{fleet_id}/members/'
    response_type = Participation

    @classmethod
    def _get(cls, fleet_id, token) -> list[Participation]:
        return cls._execute(fleet_id=fleet_id, route_args={'fleet_id': fleet_id}, token=token)

    @classmethod
    def _to_data_structure(cls, json_obj, id=None, fleet_id=None, **kwargs):
        participations = []
        for obj in json_obj:
            participations.append(
                cls.response_type.from_obj(
                    obj | ({'id': id} if id is not None and 'id' not in obj else {}) | ({'fleet_id': fleet_id} if fleet_id is not None and 'fleet_id' not in obj else {})
                )
            )
        return participations
