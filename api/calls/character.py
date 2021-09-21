from .base import CachedSwaggerAPICall, SwaggerApiCall
from data_structures.general.character import Character
from data_structures.fleet.fleet import Fleet


class CharacterFromID(CachedSwaggerAPICall):

    route = 'characters/{character_id}/'
    response_type = Character

    @classmethod
    def _get(cls, character_id, token):
        return cls._execute(id=character_id, route_args={'character_id': character_id}, token=token)


class FleetFromCharacterID(SwaggerApiCall):
    route = 'characters/{character_id}/fleet/'
    response_type = Fleet

    @classmethod
    def _get(cls, character_id, token):
        return cls._execute(route_args={'character_id': character_id}, token=token)