from datetime import datetime

from misc.crypto import get_hashed_password
from data_structures.database_object import DatabaseObject


class User(DatabaseObject):
    _table = 'users_old'

    def __repr__(self):
        return f'User {self.name}[{self.id}]'

    def __init__(
        self,
        name: str = '',
        email: str = '',
        password_hash: str = '',
        creation_time: datetime = datetime.utcnow(),
        admin: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.creation_time = creation_time
        self.admin = admin

    def set_password(self, raw_password):
        if not raw_password:
            raise Exception('Password cannot be empty!')
        self.password_hash = get_hashed_password(raw_password)

    def serialize(self) -> dict:
        return super().serialize() | {
            'name': self.name,
            'email': self.email,
            'creation_time': self.creation_time,
            'admin': self.admin
        }