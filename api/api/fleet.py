from .base import ApiObject


class CharacterFleet(ApiObject):
    """
        Simple data class to store the API response when querying for the fleet
    """
    __route__ = 'characters/{character_id}/fleet/'

    def __init__(self, fleet_id, role, squad_id, wing_id):
        self.fleet_id = fleet_id
        self.role = role
        self.squad_id = squad_id
        self.wind_id = wing_id

    @classmethod
    def _get(cls, character_id, token):
        return cls._execute(route_args={'character_id': character_id}, token=token)

    @classmethod
    def _to_data_structure(cls, json_body, init_kwargs=None, **kwargs):
        return cls(
            json_body['fleet_id'],
            json_body['role'],
            json_body['squad_id'],
            json_body['wing_id'],
        )