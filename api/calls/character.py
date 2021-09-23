from .base import CachedSwaggerAPICall, SwaggerApiCall
from data_structures.general.character import Character
from data_structures.fleet.fleet import Fleet


class CharacterFromID(CachedSwaggerAPICall):

    route = 'characters/{character_id}/'
    response_type = Character

    @classmethod
    def _get(cls, character_id):
        return cls._execute(id=character_id, route_args={'character_id': character_id})

    @classmethod
    def _args_kwargs_to_db_kwargs(self, character_id):
        return {'id': character_id}


class FleetFromCharacterID(SwaggerApiCall):
    route = 'characters/{character_id}/fleet/'
    response_type = Fleet

    @classmethod
    def _get(cls, character_id, token):
        return cls._execute(route_args={'character_id': character_id}, token=token)