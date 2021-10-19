from sqlalchemy import *
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta
from collections import defaultdict

from api.model import Base
from ..api.base import ApiObject, DATE_TIME_FORMAT


class Fleet(Base, ApiObject):
    __tablename__ = 'fleet'
    __route__ = 'fleets/{fleet_id}/'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(120))
    is_free_move = Column(Boolean)
    is_registered = Column(Boolean)
    start = Column(DateTime, default=lambda: datetime.utcnow())
    close = Column(DateTime, default=lambda: (datetime.utcnow() + timedelta(seconds=60)))

    user = relationship('User', back_populates='fleets', uselist=False)
    participations = relationship('FleetParticipation', back_populates='fleet')

    def __repr__(self):
        return f'Fleet(id={self.id}, user_id={self.user_id}, start={self.start.strftime(DATE_TIME_FORMAT)}, close={self.close.strftime(DATE_TIME_FORMAT)})'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.start:
            self.start = datetime.utcnow()
        if not self.close:
            self.close = datetime.utcnow() + timedelta(seconds=60)

    @reconstructor
    def init_on_load(self):
        if not self.start:
            self.start = datetime.utcnow()
        if not self.close:
            self.close = datetime.utcnow() + timedelta(seconds=60)

    @classmethod
    def _get(cls, fleet_id, token) -> 'Fleet':
        return cls._execute(init_kwargs={'id': fleet_id}, route_args={'fleet_id': fleet_id}, token=token)

    @classmethod
    def get_and_add(cls, session, fleet_id, token, fleet_name=None):
        try:
            fleet = session.query(Fleet).filter(Fleet.id == fleet_id).one()
        except NoResultFound:
            fleet = cls.get(fleet_id, token)
            if fleet:
                session.add(fleet)
        if not fleet.name:
            fleet.name = fleet_name
        return fleet

    @classmethod
    def _to_data_structure(cls, json_body, init_kwargs=None, **kwargs):
        return cls(
            id=init_kwargs['id'],
            is_free_move=json_body['is_free_move'],
            is_registered=json_body['is_registered'],
        )

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'is_free_move': self.is_free_move,
            'is_registered': self.is_registered,
            'start': self.start.strftime(DATE_TIME_FORMAT),
            'close': self.close.strftime(DATE_TIME_FORMAT),
            'duration_minutes': round((self.close - self.start).seconds / 60)
        }

    def update(self):
        self.close = datetime.utcnow()

    # --- Session Methods --- #

    def build_fleet_summary(self, session):
        participations_by_character = defaultdict(list)
        for participation in self.participations:
            participations_by_character[participation.character_id].append(participation)

        summary = []
        for character_id, participations in participations_by_character.items():
            character = participations[0].character

            # Get Favourite system
            systems = defaultdict(int)
            for participation in participations:
                systems[participation.system_id] += (participation.close - participation.start).seconds
            favourite_system_id = max(systems, key=systems.get)
            system = next(participation.system for  participation in participations if participation.system_id == favourite_system_id)

            # Get favourite Ship
            ships = defaultdict(int)
            for participation in participations:
                ships[participation.ship_id] += (participation.close - participation.start).seconds
            favourite_ship_id = max(ships, key=ships.get)
            ship = next(participation.ship for  participation in participations if participation.ship_id == favourite_ship_id)

            # Total attendance
            attendance_seconds = 0
            for participation in participations:
                attendance_seconds += (participation.close -participation.start).seconds

            summary.append({
                'character': character.serialize(),
                'system': system.serialize(),
                'ship': ship.serialize(),
                'attendance': round(attendance_seconds / 60)
            })

        summary = sorted(summary, key=lambda x: x['character']['name'])
        return summary

class FleetParticipation(Base, ApiObject):
    __tablename__ = 'fleet_participation'
    __route__ = 'fleets/{fleet_id}/members/'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    fleet_id = Column(BigInteger, ForeignKey('fleet.id'))
    character_id = Column(BigInteger, ForeignKey('character.id'))
    system_id = Column(BigInteger, ForeignKey('system.id'))
    ship_id = Column(BigInteger, ForeignKey('universe.id'))
    start = Column(DateTime, default=lambda: datetime.utcnow())
    close = Column(DateTime, default=lambda: (datetime.utcnow() + timedelta(seconds=60)))

    fleet = relationship('Fleet', back_populates='participations', uselist=False)
    character = relationship('Character', back_populates='fleet_participations', uselist=False)
    system = relationship('System', back_populates='fleet_participations', uselist=False)
    ship = relationship('UniverseItem', back_populates='fleet_participations', uselist=False)

    def __repr__(self):
        return f'Participation(id={self.id}, fleet_id={self.fleet_id}, character_id={self.character_id}, system_id={self.system_id}, ship_id={self.ship_id}, start={self.start.strftime(DATE_TIME_FORMAT)}, close={self.close.strftime(DATE_TIME_FORMAT)})'

    def __eq__(self, other):
        return self.fleet_id == other.fleet_id \
               and self.character_id == other.character_id \
               and self.ship_type_id == other.ship_type_id \
               and self.solar_system_id == other.solar_system_id \
               and super().__eq__(other)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.start:
            self.start = datetime.utcnow()
        if not self.close:
            self.close = datetime.utcnow() + timedelta(seconds=60)

    @reconstructor
    def init_on_load(self):
        if not self.start:
            self.start = datetime.utcnow()
        if not self.close:
            self.close = datetime.utcnow() + timedelta(seconds=60)

    @classmethod
    def _get(cls, fleet_id, token):
        return cls._execute(init_kwargs={'fleet_id': fleet_id}, route_args={'fleet_id': fleet_id}, token=token)

    @classmethod
    def _to_data_structure(cls, json_body, init_kwargs=None, **kwargs):
        return [cls(
            fleet_id=init_kwargs['fleet_id'],
            character_id=j['character_id'],
            system_id=j['solar_system_id'],
            ship_id=j['ship_type_id'],
        ) for j in json_body]

    def update(self):
        self.close = datetime.utcnow()
