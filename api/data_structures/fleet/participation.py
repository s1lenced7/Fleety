from typing import Union
from datetime import datetime
from collections import defaultdict

from ...constants import DATE_FORMAT
from ..general.character import Character
from ..base import TimetrackedObject, ApiObject, DatabaseObject


# class ParticipationSummary:
#     """"""
#
#     @classmethod
#     def from_fleet_id(cls, fleet_id):
#         participations = list(Participation.from_db(fleet_id=fleet_id))


class Participation(TimetrackedObject, ApiObject, DatabaseObject):
    _table = 'participation'
    _route = 'fleets/{fleet_id}/members/'

    @classmethod
    def _get(cls, fleet_id, token) -> list['Participation']:
        return cls._execute(fleet_id=fleet_id, route_args={'fleet_id': fleet_id}, token=token)

    @classmethod
    def summary_from_participations(cls, participations):
        t = 5
        # Group by character
        participations_by_character = defaultdict(list)
        for participation in participations:
            participations_by_character[participation.character_id].append(participation)

        for character_id, character_participations in participations_by_character.items():
            character = Character.get_from_id(character_id)

    def __repr__(self):
        return f'Participation {{' \
               f'Fleet: {self.fleet_id}, ' \
               f'Character: {self.character_id}, ' \
               f'Ship: {self.ship_type_id}, ' \
               f'System: {self.solar_system_id}' \
               f'}} {super().__repr__()}'

    def __init__(
            self,
            fleet_id: int = -1,
            character_id: int = -1,
            ship_type_id: int = -1,
            solar_system_id: int = -1,
            *,
            join_time: Union[datetime, str] = datetime.now(),
            **kwargs
    ):
        super().__init__(**kwargs)

        self.fleet_id = fleet_id
        self.character_id = character_id
        self.ship_type_id = ship_type_id
        self.solar_system_id = solar_system_id

        self.join_time = join_time
        if isinstance(self.join_time, str):
            self.join_time = datetime.strptime(join_time, DATE_FORMAT)

    def __eq__(self, other: 'Participation'):
        """
        Participations are considered equal as long as the character is:
            - In the same System
            - Flying the same vessel
            - The other participation was less than a specific period ago
        """
        return self.fleet_id == other.fleet_id \
               and self.character_id == other.character_id \
               and self.ship_type_id == other.ship_type_id \
               and self.solar_system_id == other.solar_system_id \
               and super().__eq__(other)
