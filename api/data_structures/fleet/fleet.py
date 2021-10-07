from collections import defaultdict

from ...constants import DATE_FORMAT
from ..base import TimetrackedObject, StoredApiObject, ApiObject
from .participation import Participation


class Fleet(TimetrackedObject, StoredApiObject):
    _table = 'fleet'
    _route = 'fleets/{fleet_id}/'

    @staticmethod
    def _get_kwargs_to_db_kwargs(route_args, **kwargs):
        return {'id': route_args['fleet_id']}

    @classmethod
    def _get(cls, fleet_id, token) -> 'Fleet':
        return cls._execute(id=fleet_id, route_args={'fleet_id': fleet_id}, token=token)

    def __repr__(self):
        return f'Fleet[{self.id}] - {super().__repr__()}'

    def __init__(
            self,
            is_free_move: bool = False,
            is_registered: bool = False,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.is_free_move = is_free_move
        self.is_registered = is_registered
        self.participations = defaultdict(list)
        self.user_id = None

    def __eq__(self, other: 'Fleet'):
        return issubclass(type(other), type(self)) and self.id == other.id

    def serialize(self, *args, **kwargs) -> dict:
        return super().serialize() | {
            'user_id': self.user_id,
            # 'name': self.name, TODO
            'duration': self.duration,
            'start': self.start.strftime(DATE_FORMAT),
            'close': self.close.strftime(DATE_FORMAT),
        }

    def update_participations(self, new_participations: list[Participation]):
        """
        Adds and or updates fleet participations based on a snapshot of fleet participations

        TODO: What if new participation is younger than the previous, Handle gracefully
        """
        for new_participation in new_participations:
            character_participations = self.participations[new_participation.character_id]
            if character_participations and character_participations[-1] == new_participation:
                character_participations[-1].update()
            else:
                self.participations[new_participation.character_id].append(new_participation)
        self._persist_participaitons()

    def _persist_participaitons(self):
        """
        # TODO make these more efficient, now you'll update a row even if the character has left hours ago!
        """
        participations_to_update = []
        for character, participations in self.participations.items():
            participations_to_update.append(participations[-1])  # TODO:Could this error?
        Participation.bulk_write_to_db(participations_to_update)


class CharacterFleet(ApiObject):
    """
        Simple data class to store the API response when querying for the fleet
    """
    _route = 'characters/{character_id}/fleet/'

    def __init__(
            self,
            fleet_id: bool = False,
            **kwargs
    ):
        super().__init__(id=fleet_id, **kwargs)

    @classmethod
    def _get(cls, character_id, token):
        return cls._execute(route_args={'character_id': character_id}, token=token)
