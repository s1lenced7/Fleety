from copy import copy
from sqlalchemy import *
from sqlalchemy.orm import relationship

from api.model import Base
from ..api.base import ApiObject


class UniverseItem(Base, ApiObject):
    __tablename__ = 'universe'
    __route__ = 'universe/names/'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    category = Column(String(120))
    name = Column(String(120))
    fleet_participations = relationship('FleetParticipation', back_populates='ship')

    def __repr__(self):
        return f'UniverseItem(id={self.id}, name={self.name}, category={self.category})'

    @classmethod
    def _get(cls, ids):
        return cls._execute(json_request_body=ids)

    @classmethod
    def get_and_add(cls, session, ids):
        ids = copy(ids)
        if not isinstance(ids, list):
            ids = [ids]

        universe_items = session.query(UniverseItem).filter(UniverseItem.id.in_(ids)).all()
        for universe_item in universe_items:
            ids.remove(universe_item.id)
        if not ids:
            return universe_items

        api_universe_items = cls.get(ids)
        for api_universe_item in api_universe_items:
            session.add(api_universe_item)
        return universe_items + api_universe_items

    @classmethod
    def _to_data_structure(cls, json_body, init_kwargs=None, **kwargs):
        return [cls(
            id=j['id'],
            name=j['name'],
            category=j['category'],
        ) for j in json_body]

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
        }