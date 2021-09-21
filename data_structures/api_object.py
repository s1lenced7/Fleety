import json
from uuid import uuid4
from copy import deepcopy
from datetime import datetime

from misc.exceptions import EmbeddedException


class ApiObjectCreationError(EmbeddedException):
    """"""


class HistoricalAttribute:

    def __init__(self, type):
        self._value = None
        self._type = type
        self._history = {}

    def set(self, value):
        if type(value) != self._type:
            raise TypeError(f'Tried setting `{type(value)}`, expected `{self._type}`')
        self._value = value
        self._history[datetime.utcnow()] = self._value

    def get(self):
        return deepcopy(self._value)


class ApiObject:
    select_query = None

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

    def __init__(self, id=None, **kwargs):
        self.id = id if id is not None else str(uuid4())


class TimetrackedApiObject(ApiObject):
    MAX_TIMEOUT = 5 * 60

    def __eq__(self, other: 'TimetrackedApiObject'):
        return (other._start - self._close).seconds < self.MAX_TIMEOUT

    def __repr__(self):
        return f'[{self._start.strftime("%Y-%m-%d %H:%M:%S")}UTC - {self._close.strftime("%Y-%m-%d %H:%M:%S")}UTC]'

    def __init__(self, *args, start: datetime = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._start = datetime.utcnow()
        self._close = datetime.utcnow()
        if start:
            self._start = start

    def update(self):
        self._close = datetime.utcnow()
