import json
from datetime import datetime
from base64 import b64decode

from api.api_object import ApiObject
from api.oauth.calls import oauth_refresh_token, oauth_get_token
from misc.exceptions import EmbeddedException


class ClientToken(ApiObject):
    eager_refresh_time = 60
    min_time_before_refresh = 60

    @staticmethod
    def explode_token(token):
        return json.loads(b64decode(token.split('.')[1].replace('-', '+').replace('_', '/')))

    @classmethod
    def from_oauth_code(cls, code):
        return cls.from_obj(oauth_get_token(code))

    def __init__(
            self,
            access_token: str = None,
            expires_in: int = 0,
            token_type: str = 'Bearer',
            refresh_token: str = None,
            **kwargs
    ):
        super().__init__(**kwargs)

        self._access_token = access_token
        self.type = token_type
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self._creation_time = datetime.utcnow()
        self._last_update_attempt = None

    @property
    def expired(self):
        return (datetime.utcnow() - self._creation_time).seconds >= (self.expires_in - self.eager_refresh_time)

    @property
    def access_token(self):
        if self.expired:
            self.refresh_access_token()
        return self._access_token

    def character_id(self):
        try:
            json_token = self.explode_token(self._access_token)
            character_sub = int(json_token['sub'].split(':')[-1])
            return character_sub
        except Exception as ex:
            raise EmbeddedException('Failed to extract character id from JWT', exception=ex)

    def refresh_access_token(self):
        if self._last_update_attempt and (datetime.utcnow() - self._last_update_attempt).seconds >= self.min_time_before_refresh:
            raise Exception('Not enough time has passes since attempting to refresh token!')
        self._last_update_attempt = datetime.utcnow()

        try:
            obj = oauth_refresh_token(self.refresh_token)
        except Exception as ex:
            raise EmbeddedException('Token Refresh request failed!', exception=ex)

        ref_token = ClientToken.from_obj(obj)
        self._access_token = ref_token._access_token
        self.type = ref_token.type
        self.expires_in = ref_token.expires_in
        self.refresh_token = ref_token.refresh_token
        self._creation_time = datetime.utcnow()