import json
from requests import request
from abc import ABC, abstractmethod
from misc.exceptions import EmbeddedException

from api.cache import API_CACHES, args_kwargs_to_cache_key
from api.api_object import ApiObject

GET = 'GET'
POST = 'POST'


class SwaggerAPIError(EmbeddedException):
    """"""


class UnexpectedStatusCode(SwaggerAPIError):

    def __init__(self, *args, status_code=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status_code


class JsonDecompressionFailure(SwaggerAPIError):
    """"""


class SwaggerApiCall(ABC):
    domain = 'esi.evetech.net'
    datasource = 'tranquility'
    branch = 'latest'
    requires_authentication = False
    response_codes = [200]
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
    }

    route = None
    response_type: ApiObject = None

    @classmethod
    def _build_url(cls, route_args=None, parameters=None):
        if not route_args:
            route_args = {}
        if not parameters:
            parameters = {}

        route = cls.route.format(**route_args)
        return f'https://{cls.domain}/{cls.branch}/{route}?' + '&'.join(
            f'{key}={val}'
            for key, val in (parameters | {'datasource': cls.datasource}).items()
        )

    @classmethod
    def _do_request(cls, json_body=None, headers=None, token=None, **kwargs):
        if not headers:
            headers = {}
        if token:
            headers['Authorization'] = f'{token.type} {token.access_token}'

        return request(
            url=cls._build_url(**kwargs),
            method=POST if json_body else GET,
            headers=headers | cls.headers,
            data=json.dumps(json_body) if json_body else None
        )

    @classmethod
    @abstractmethod
    def _get(cls, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def get(cls, *args, **kwargs):
        return cls._get(*args, **kwargs)

    @classmethod
    def _execute(cls, *args, id=None, **kwargs):

        try:
            result = cls._do_request(*args, **kwargs)
        except Exception as ex:
            raise EmbeddedException('Failed to complete api call', exception=ex)

        if result.status_code not in cls.response_codes:
            raise UnexpectedStatusCode(f'Got unexpected Status Code {result.status_code}', status_code=result.status_code)

        try:
            result = json.loads(result.text)
        except Exception as ex:
            raise JsonDecompressionFailure('Failed to decompress ', exception=ex)

        # A bit of a hack, but i wanted this to work
        return cls._to_data_structure(result, id)

    @classmethod
    def _to_data_structure(cls, json_obj, id=None):
        return cls.response_type.from_obj(json_obj | ({'id': id} if id is not None and 'id' not in json_obj else {}))


class CachedSwaggerAPICall(SwaggerApiCall):
    """
    The key method is not fool proof but it works for what we want to do with it
    """

    @classmethod
    def get(cls, *args, **kwargs):
        cache = API_CACHES[cls]

        cache_key = args_kwargs_to_cache_key(*args, **kwargs)
        result = cache.get(cache_key)
        if not result:
            result = cls._get(*args, **kwargs)
            cache[cache_key] = result
        return result
