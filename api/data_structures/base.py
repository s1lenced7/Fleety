import json
from uuid import uuid4
from requests import request
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from misc.exceptions import EmbeddedException
from typing import Iterable
from database.connection import MySQLConnectionManager
from database.constants import DB_NAME


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


class ApiObjectCreationError(EmbeddedException):
    """"""


class BaseObject(ABC):

    @classmethod
    def from_json(cls, raw_json, *args):
        try:
            obj = json.loads(raw_json)
        except Exception as ex:
            raise ApiObjectCreationError(f'Failed to create instance from Json', ex)
        return cls.from_obj(obj, *args)

    @classmethod
    def from_json_list(cls, raw_json, *args):
        try:
            instances = []
            obj = json.loads(raw_json)
            for sub_obj in obj:
                instances.append(cls.from_obj(sub_obj, *args))
            return instances
        except Exception as ex:
            raise ApiObjectCreationError(f'Failed to create instance list from Json', ex)

    @classmethod
    def from_obj(cls, obj: dict, *args):
        try:
            return cls(*args, **obj)
        except Exception as ex:
            raise ApiObjectCreationError('Failed to populate instance from obj', ex)

    @classmethod
    def _to_data_structure(cls, json_objs, id=None):
        data = []
        if not json_objs:
            return []
        if not isinstance(json_objs, list):
            json_objs = [json_objs]
        for json_obj in json_objs:
            data.append(
                cls.from_obj(
                    json_obj | ({'id': id} if id is not None and 'id' not in json_obj else {})
                )
            )
        return data

    def __init__(self, id=None, **kwargs):
        self.id = id if id is not None else str(uuid4())

    def serialize(self, *args, **kwargs) -> dict:
        return {'id': self.id}

class TimetrackedObject:
    MAX_TIMEOUT = 5 * 60

    def __eq__(self, other: 'TimetrackedObject'):
        return (other.start - self.close).seconds < self.MAX_TIMEOUT

    def __repr__(self):
        return f'<{self.start.strftime("%Y-%m-%d %H:%M:%S")}UTC - {self.close.strftime("%Y-%m-%d %H:%M:%S")}UTC>'

    def __init__(self, *args, start: datetime = None, close=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not start:
            start = datetime.utcnow()
        self.start = start

        if not close:
            close = datetime.utcnow() + timedelta(seconds=60)
        self.close = close

    @property
    def duration(self):
        return round((self.close - self.start).seconds / 60)

    def update(self):
        self.close = datetime.utcnow()


class ApiObject(BaseObject, ABC):
    domain = 'esi.evetech.net'
    datasource = 'tranquility'
    branch = 'latest'
    requires_authentication = False
    response_codes = [200]
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
    }

    _route = None

    @classmethod
    @abstractmethod
    def _get(cls, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def get(cls, *args, **kwargs):
        return iter(cls._get(*args, **kwargs))

    @classmethod
    def _build_url(cls, route_args=None, parameters=None, **kwargs):
        if not route_args:
            route_args = {}
        if not parameters:
            parameters = {}

        route = cls._route.format(**route_args)
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

        # TODO: DEBUG LOGGING
        url = cls._build_url(**kwargs)
        print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Calling: {url}')
        return request(
            url=url,
            method=POST if json_body else GET,
            headers=headers | cls.headers,
            data=json.dumps(json_body) if json_body else None
        )

    @classmethod
    def _execute(cls, id=None, **kwargs):
        try:
            try:
                result = cls._do_request(**kwargs)
            except Exception as ex:
                raise EmbeddedException('Failed to complete api call', exception=ex)

            if result.status_code not in cls.response_codes:
                raise UnexpectedStatusCode(f'Got unexpected Status Code {result.status_code}',
                                           status_code=result.status_code)

            try:
                result = json.loads(result.text)
            except Exception as ex:
                raise JsonDecompressionFailure('Failed to decompress ', exception=ex)

            # A bit of a hack, but i wanted this to work
            return cls._to_data_structure(result, id)
        except Exception as ex:
            # TODO, for now i'll print the error and return None so the app can continue
            #       FIX LOGGING!!!!
            print(f'API call error, {ex}, continuing')
            return None


class DatabaseObject(BaseObject, ABC):
    _table = None
    _column_names = None
    _read_query = 'SELECT * FROM {db_name}.{table} '
    _write_query = 'REPLACE INTO {db_name}.{table} VALUES {values}'
    _remove_query = 'DELETE FROM {db_name}.{table} '

    @classmethod
    def _get_column_names(cls):
        # TODO: possibly cache this info, this does mean restarting the web-app when data-base is updated
        if not cls._column_names:
            column_names = []
            with MySQLConnectionManager.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f'describe {DB_NAME}.{cls._table}')
                    for column_info in cursor:
                        column_names.append(column_info[0])
            cls._column_names =column_names
        return cls._column_names

    @classmethod
    def _get_rows(cls, **kwargs):
        columns = cls._get_column_names()
        for key, value in kwargs.items():
            if key not in columns:
                raise KeyError(f'`{key}` is not a valid column in `{cls._table}`')

        query = cls._read_query.format(db_name=DB_NAME, table=cls._table)
        parameters = []
        if kwargs:
            query += 'WHERE '
            additions = []
            for key, value in kwargs.items():
                if isinstance(value, Iterable) and not isinstance(value, str):
                    additions.append(f'{key} in ({", ".join("%s" for _ in range(0, len(value)))}) ')
                    parameters += list(value)
                else:
                    additions.append(f'{key} = %s ')
                    parameters.append(value)
            query += 'AND '.join(additions)

        rows = []
        with MySQLConnectionManager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(parameters))
                for row in cursor:
                    rows.append({columns[idx]: column_value for idx, column_value in enumerate(row)})
        return rows

    @classmethod
    def bulk_remove_from_db(cls, instances: list['DatabaseObject']):
        # TODO cleanup
        if not instances:
            return

        kwargs = {'id': [instance.id for instance in instances]}
        columns = cls._get_column_names()
        for key, value in kwargs.items():
            if key not in columns:
                raise KeyError(f'`{key}` is not a valid column in `{cls._table}`')

        query = cls._remove_query.format(db_name=DB_NAME, table=cls._table)
        query += f'WHERE id in ({", ".join("%s" for _ in range(0, len(instances)))})'
        with MySQLConnectionManager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(kwargs['id']))
            connection.commit()

    @classmethod
    def bulk_write_to_db(cls, instances):
        if not instances:
            return

        value_sets = []
        for instance in instances:
            values = instance._obj_to_db_values()
            if not values:
                raise Exception('Need values to insert into table')
            value_sets.append(values)

        value_str = ', '.join(
            '(' + ', '.join('%s' for _ in range(len(value_set))) + ')'
            for value_set in value_sets
        )
        # TODO: DEBUG LOGGING
        print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Writing to DB')
        query = cls._write_query.format(
            db_name=DB_NAME,
            table=cls._table,
            values=value_str
        )
        try:
            with MySQLConnectionManager.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, tuple([value for value_set in value_sets for value in value_set]))
                connection.commit()
        except Exception as ex:
            raise EmbeddedException('Failed to insert new rows', exception=ex)

    @classmethod
    def from_db(cls, **kwargs):
        return iter(cls._to_data_structure(cls._get_rows(**kwargs)))

    def write_to_db(self):
        return self.bulk_write_to_db([self])

    def remove_from_db(self):
        self.bulk_remove_from_db([self])

    def _obj_to_db_values(self):
        values = []
        for column in self._get_column_names():
            values.append(getattr(self, column))
        return values


class StoredApiObject(ApiObject, DatabaseObject):
    _cached = False

    @staticmethod
    def _get_kwargs_to_db_kwargs(*args, **kwargs) -> dict:
        raise NotImplementedError

    @classmethod
    def _execute(cls, id=None, **kwargs):
        results = list(cls.from_db(**cls._get_kwargs_to_db_kwargs(**kwargs)))
        if not results:
            api_results = super()._execute(id=id, **kwargs)
            cls.bulk_write_to_db(api_results)
            results += api_results
        return iter(results)
