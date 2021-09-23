from collections import defaultdict
from data_structures.api_object import TimetrackedApiObject

from .participation import Participation


class Fleet(TimetrackedApiObject):

    def __repr__(self):
        return f'Fleet[{self.id}] - {super().__repr__()}'

    def __init__(
            self,
            fleet_id: int,
            *,
            is_free_move: bool = False,
            is_registered: bool = False,
            is_voice_enabled: bool = False,
            motd: str = '',
            **kwargs
    ):
        super().__init__(id=fleet_id, **kwargs)
        self.is_free_move = is_free_move
        self.is_registered = is_registered
        self.is_voice_enabled = is_voice_enabled
        self.motd = motd
        self.participations = defaultdict(list)

    def __eq__(self, other: 'Fleet'):
        return issubclass(type(other), type(self)) and self.id == other.id

    def update_participations(self, new_participations: list[Participation]):
        """
        Adds and or updates fleet participations based on a snapshot of fleet participations

        TODO: What if new participation is younger than the previous, Handle the gracefully
        """
        for new_participation in new_participations:
            character_participations = self.participations[new_participation.character_id]
            if character_participations and character_participations[-1] == new_participation:
                character_participations[-1].update()
            else:
                self.participations[new_participation.character_id].append(new_participation)