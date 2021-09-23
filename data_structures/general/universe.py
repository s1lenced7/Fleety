from data_structures.api_object import ApiObject
from data_structures.database_object import DatabaseObject


class UniverseItem(ApiObject, DatabaseObject):
    _table = 'universe'

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
