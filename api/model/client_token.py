import json
from datetime import datetime
from base64 import b64decode

from sqlalchemy import *
from sqlalchemy.orm import relationship, reconstructor

from api.model import Base
from ..api.oauth import oauth_refresh_token, oauth_get_token
from misc.exceptions import EmbeddedException


class ClientToken(Base):
    __tablename__ = 'client_token'

    eager_refresh_time = 60
    min_time_before_refresh = 60

    id = Column(BigInteger, primary_key=True)
    character_id = Column(BigInteger, ForeignKey('character.id'))
    character = relationship("Character", back_populates="client_token", uselist=False)
    refresh_token = Column(String(120))

    def __init__(self, *args, access_token=None, expires_in=0, **kwargs):
        super().__init__(*args, **kwargs)
        self._access_token = access_token
        self.expires_in = expires_in
        self._creation_time = datetime.utcnow()
        self._last_update_attempt = None

    @reconstructor
    def init_on_load(self):
        self._access_token = None
        self.expires_in = 0
        self._creation_time = datetime.utcnow()
        self._last_update_attempt = None

    @staticmethod
    def explode_token(token):
        b64 = token.split('.')[1].replace('-', '+').replace('_', '/')
        try:
            return json.loads(b64decode(b64))
        except Exception:
            # commence eye rolling, incorrect padding is possible!
            return json.loads(b64decode(b64 + '='))

    @classmethod
    def character_id_from_token(cls, token):
        try:
            json_token = cls.explode_token(token)
            character_sub = int(json_token['sub'].split(':')[-1])
            return character_sub
        except Exception as ex:
            raise EmbeddedException('Failed to extract character id from JWT', exception=ex)

    @classmethod
    def from_oauth_code(cls, code):
        json_body = oauth_get_token(code)
        return cls(
            character_id=cls.character_id_from_token(json_body['access_token']),
            refresh_token=json_body['refresh_token'],
            access_token=json_body['access_token'],
            expires_in=json_body['expires_in']
        )

    @property
    def expired(self):
        return (datetime.utcnow() - self._creation_time).seconds >= (self.expires_in - self.eager_refresh_time)

    @property
    def access_token(self):
        if self.expired:
            self.refresh_access_token()
        return self._access_token

    def refresh_access_token(self):
        if self.refresh_token is None:
            return

        if self._last_update_attempt and (datetime.utcnow() - self._last_update_attempt).seconds <= self.min_time_before_refresh:
            raise Exception('Not enough time has passes since attempting to refresh token!')
        self._last_update_attempt = datetime.utcnow()

        try:
            obj = oauth_refresh_token(self.refresh_token)
        except Exception as ex:
            raise EmbeddedException('Token Refresh request failed!', exception=ex)

        self._access_token = obj['access_token']
        self.refresh_token = obj['refresh_token']
        self.expires_in = obj['expires_in']
        self._creation_time = datetime.utcnow()