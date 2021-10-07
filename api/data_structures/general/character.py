from typing import Union
from datetime import datetime

from api.data_structures.oauth.token import ClientToken
from ...constants import DATE_FORMAT
from ..base import StoredApiObject


class Character(StoredApiObject):
    _table = 'character'
    _route = 'characters/{character_id}/'

    @staticmethod
    def _get_kwargs_to_db_kwargs(route_args, **kwargs):
        return {'id': route_args['character_id']}

    @classmethod
    def _get(cls, character_id):
        return cls._execute(id=character_id, route_args={'character_id': character_id})

    def __repr__(self):
        return f'Character {self.name}[{self.id}]'

    def __init__(
        self,
        user_id: int = None,
        name: str = '',
        birthday: Union[datetime, str] = datetime.now(),
        bloodline_id: int = -1,
        corporation_id: int = -1,
        # We will not bother storing expensive descriptions
        # description: str = "",
        race_id: int = -1,
        security_status: float = 0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.name = name
        self.birthday = birthday
        if type(birthday) == str:
            self.birthday = datetime.strptime(self.birthday, DATE_FORMAT)
        self.bloodline_id = bloodline_id
        self.corporation_id = corporation_id
        self.race_id = race_id
        self.security_status = security_status

    def get_auth_token(self):
        return next(ClientToken.from_db(character_id=self.id), None)

    def serialize(self, *args, **kwargs) -> dict:
        return super().serialize() | {
            'user_id': self.user_id,
            'name': self.name,
            'birthday': self.birthday.strftime(DATE_FORMAT),
            'bloodline_id': self.bloodline_id,
            'corporation_id': self.corporation_id,
            'race_id': self.race_id,
            'security_status': self.security_status,
        }