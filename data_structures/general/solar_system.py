from api.api_object import ApiObject

class SolarSystem(ApiObject):

    def __repr__(self):
        return f'Solar System {self.name}[{self.id}]'

    def __init__(
        self,
        system_id: int = None,
        name: str = '',
        security_status: float = 0.0,
        **kwargs,
    ):
        super().__init__(id=system_id, **kwargs)
        self.name = name
        self.security_status = security_status
