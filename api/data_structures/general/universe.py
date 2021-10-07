from copy import copy
from ..base import StoredApiObject


class UniverseItem(StoredApiObject):
    _table = 'universe'
    _route = 'universe/names/'

    @classmethod
    def _get(cls, ids):
        return cls._execute(json_body=ids)

    @staticmethod
    def _get_kwargs_to_db_kwargs(json_body, **kwargs):
        return {'id': json_body}

    def __repr__(self):
        return f'UniverseItem({self.category}) {self.name}[{self.id}]'

    def __init__(
        self,
        category: int = 0,
        name: str = '',
        **kwargs,
    ):
        super().__init__( **kwargs)
        self.category = category
        self.name = name

    @classmethod
    def _execute(cls, id=None, **kwargs):
        results = cls.from_db(**cls._get_kwargs_to_db_kwargs(**kwargs), default=[])
        _kwargs = copy(kwargs)
        for result in results:
            _kwargs['json_body'].remove(result.id)
        if _kwargs['json_body']:
            api_results = super(StoredApiObject, cls)._execute(**_kwargs)
            cls.bulk_write_to_db(api_results)
            results += api_results
        return results