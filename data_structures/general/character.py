from typing import Union
from datetime import datetime

from api.api_object import ApiObject
from api.constants import DATE_FORMAT


class Character(ApiObject):

    def __repr__(self):
        return f'Character {self.name}[{self.id}]'

    def __init__(
        self,
        name: str = '',
        birthday: Union[datetime, str] = datetime.now(),
        bloodline_id: int = -1,
        corporation_id: int = -1,
        description: str = "",
        race_id: int = -1,
        security_status: float = 0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.name = name
        self.birthday = birthday
        if type(birthday) == str:
            self.birthday = datetime.strptime(self.birthday, DATE_FORMAT)
        self.bloodline_id = bloodline_id
        self.corporation_id = corporation_id
        self.description = description
        self.race_id = race_id
        self.security_status = security_status