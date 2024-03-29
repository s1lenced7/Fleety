import json
import requests
from datetime import datetime
from uuid import uuid4
from urllib.parse import quote
from requests.auth import HTTPBasicAuth

from .exception import OAuthRefreshException, OAuthException

# As of unhiding these credentials have been discarded and are no-longer valid
CLIENT_ID = 'client_id_here'
CLIENT_SECRET = 'client_secret_here'
CALL_BACK_URL = quote('http://178.117.200.140:8080/characters/link_callback')
SCOPES = ['esi-fleets.read_fleet.v1']


def oauth_redirect_url():
    return f'https://login.eveonline.com/v2/oauth/authorize?' \
           f'response_type=code' \
           f'&redirect_uri={CALL_BACK_URL}' \
           f'&client_id={CLIENT_ID}' \
           f'&scope={" ".join(quote(scope) for scope in SCOPES)}' \
           f'&state={uuid4().hex}'


def oauth_get_token(code):
    try:
        response = requests.post(
            url='https://login.eveonline.com/v2/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'code': code
            },
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'login.eveonline.com',
            }
        )
        if response.status_code != 200:
            raise OAuthRefreshException('Oauth token fetch request failed!', status_code=response.status_code)
        return json.loads(response.text)
    except Exception as ex:
        raise OAuthException('Oauth token fetch failed!', exception=ex)


def oauth_refresh_token(refresh_token):
    """
    POST https://login.eveonline.com/v2/oauth/token HTTP/1.1

    Content-Type:
    Host:
    Authorization: Basic QWxhZGRpbjpPcGVuU2VzYW1l

    grant_type=refresh_token&refresh_token=gEy...fM0
    :return:
    """
    # TODO: DEBUG LOGGING
    print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Attempting to Refresh OAuthToken')
    try:
        response = requests.post(
            url='https://login.eveonline.com/v2/oauth/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            },
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'login.eveonline.com',
            }
        )
        if response.status_code != 200:
            raise OAuthRefreshException('Oauth token refresh request failed!', status_code=response.status_code)
        return json.loads(response.text)
    except Exception as ex:
        raise OAuthException('Oauth token refresh failed!', exception=ex)


def oauth_invalidate_token(refresh_token):
    # TODO: DEBUG LOGGING
    print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Attempting to invalidate OAuthToken')
    try:
        response = requests.post(
            url='https://login.eveonline.com/v2/oauth/revoke',
            data={
                'token_type_hint': 'refresh_token',
                'token': refresh_token
            },
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'login.eveonline.com',
            }
        )
        if response.status_code != 200:
            raise OAuthRefreshException('Oauth token invalidation request failed!', status_code=response.status_code)
    except Exception as ex:
        raise OAuthException('Oauth token invalidation failed!', exception=ex)
