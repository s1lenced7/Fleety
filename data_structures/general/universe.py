from api.api_object import ApiObject


class UniverseItem(ApiObject):

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
