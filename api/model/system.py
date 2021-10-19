from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.exc import NoResultFound

from api.model import Base
from ..api.base import ApiObject


class System(Base, ApiObject):
    __tablename__ = 'system'
    __route__ = 'universe/systems/{system_id}/'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    name = Column(String(120))
    security_status = Column(Float)

    fleet_participations = relationship('FleetParticipation', back_populates='system')

    def __repr__(self):
        return f'Solar System(id={self.id}, name={self.name})'

    @classmethod
    def _get(cls, system_id):
        return cls._execute(route_args={'system_id': system_id})

    @classmethod
    def get_and_add(cls, session, system_id):
        try:
            system = session.query(System).filter(System.id == system_id).one()
            if system:
                return system
        except NoResultFound:
            system = cls.get(system_id)
            if system:
                session.add(system)
        return system

    @classmethod
    def _to_data_structure(cls, json_body, init_kwargs=None, **kwargs):
        return cls(
            id=json_body['system_id'],
            name=json_body['name'],
            security_status=json_body['security_status'],
        )

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'security_status': self.security_status,
        }