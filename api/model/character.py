from sqlalchemy import *
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship
from datetime import datetime

from api.model import Base
from ..api import DATE_TIME_FORMAT, ApiObject, CharacterFleet


class Character(Base, ApiObject):
    __tablename__ = 'character'
    __route__ = 'characters/{character_id}/'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    name = Column(String(120))
    birthday = Column(DateTime)
    bloodline = Column(Integer)
    corporation = Column(Integer)
    race = Column(Integer)
    security_status = Column(Float)

    user = relationship('User', back_populates='characters', uselist=False)
    client_token = relationship('ClientToken', back_populates='character', uselist=False)
    fleet_participations = relationship('FleetParticipation', back_populates='character')

    def __repr__(self):
        return f"Character(id={self.id!r}, name={self.name!r})"

    @classmethod
    def _get(cls, character_id):
        return cls._execute(init_kwargs={'id': character_id}, route_args={'character_id': character_id})

    @classmethod
    def _to_data_structure(cls, json_body, init_kwargs=None, **kwargs):
        return cls(
            id=init_kwargs['id'],
            name=json_body['name'],
            birthday=datetime.strptime(json_body['birthday'], DATE_TIME_FORMAT),
            bloodline=json_body['bloodline_id'],
            corporation=json_body['corporation_id'],
            race=json_body['race_id'],
            security_status=json_body['security_status'],
        )

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'birthday': self.birthday.strftime(DATE_TIME_FORMAT),
            'bloodline_id': self.bloodline,
            'corporation_id': self.corporation,
            'race_id': self.race,
            'security_status': self.security_status,
        }

    # --- Session Methods --- #

    @classmethod
    def get_and_add(cls, session, character_id):
        try:
            character = session.query(Character).filter(Character.id == character_id).one()
            if character:
                return character
        except NoResultFound:
            character = cls.get(character_id)
            if character:
                session.add(character)
        return character

    def get_fleet_id(self):
        client_token = self.client_token
        fleet_id = None
        if not client_token:
            return fleet_id

        try:
            cf = CharacterFleet.get(self.id, client_token)
            fleet_id = cf.fleet_id
        except Exception:
            pass
        return fleet_id
