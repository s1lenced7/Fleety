from .base import SwaggerApiCall
from data_structures.general.solar_system import SolarSystem


class SolarSystemFromID(SwaggerApiCall):

    route = 'universe/systems/{solar_system_id}/'
    response_type = SolarSystem

    @classmethod
    def _get(cls, solar_system_id):
        return cls._execute(route_args={'solar_system_id': solar_system_id})