from ..base import StoredApiObject


class SolarSystem(StoredApiObject):
    _table = 'solar_system'
    _route = 'universe/systems/{system_id}/'

    @staticmethod
    def _get_kwargs_to_db_kwargs(route_args, **kwargs):
        return {'system_id': route_args['system_id']}

    @classmethod
    def _get(cls, solar_system_id):
        return cls._execute(route_args={'system_id': solar_system_id})

    def __repr__(self):
        return f'Solar System {self.name}[{self.id}]'

    def __init__(
        self,
        system_id: int = None,
        name: str = '',
        security_status: float = 0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.system_id = system_id
        self.name = name
        self.security_status = security_status
