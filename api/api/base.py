import json
from datetime import datetime
from requests.api import request

from .exception import EmbeddedException

GET = 'GET'
POST = 'POST'
DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class SwaggerAPIError(EmbeddedException):
    """"""


class UnexpectedStatusCode(SwaggerAPIError):

    def __init__(self, *args, status_code=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status_code


class JsonDecompressionFailure(SwaggerAPIError):
    """"""


class ApiObjectCreationError(EmbeddedException):
    """"""


class ApiObject:
    _domain = 'esi.evetech.net'
    _datasource = 'tranquility'
    _branch = 'latest'
    _requires_authentication = False
    _response_codes = [200]
    _headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
    }

    __route__ = None

    @classmethod
    def _to_data_structure(cls, json_body, init_kwargs=None, **kwargs):
        raise NotImplementedError()

    @classmethod
    def _get(cls, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def get(cls, *args, **kwargs):
        return cls._get(*args, **kwargs)

    @classmethod
    def _build_url(cls, route_args=None, parameters=None, **kwargs):
        if not route_args:
            route_args = {}
        if not parameters:
            parameters = {}

        route = cls.__route__.format(**route_args)
        return f'https://{cls._domain}/{cls._branch}/{route}?' + '&'.join(
            f'{key}={val}'
            for key, val in (parameters | {'datasource': cls._datasource}).items()
        )

    @classmethod
    def _do_request(cls, json_request_body=None, headers=None, token=None, **kwargs):
        if not headers:
            headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token.access_token}'

        # TODO: DEBUG LOGGING
        url = cls._build_url(**kwargs)
        print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Calling: {url}')
        return request(
            url=url,
            method=POST if json_request_body else GET,
            headers=headers | cls._headers,
            data=json.dumps(json_request_body) if json_request_body else None
        )

    @classmethod
    def _execute(cls, **kwargs):
        try:
            try:
                result = cls._do_request(**kwargs)
            except Exception as ex:
                raise EmbeddedException('Failed to complete api call', exception=ex)

            if result.status_code not in cls._response_codes:
                raise UnexpectedStatusCode(f'Got unexpected Status Code {result.status_code}',
                                           status_code=result.status_code)

            try:
                result = json.loads(result.text)
            except Exception as ex:
                raise JsonDecompressionFailure('Failed to decompress ', exception=ex)

            # A bit of a hack, but i wanted this to work
            return cls._to_data_structure(result, **kwargs)
        except Exception as ex:
            # TODO, for now i'll print the error and return None so the app can continue
            #       FIX LOGGING!!!!
            print(f'API call error, {ex}, continuing')
            return None