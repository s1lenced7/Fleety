from sqlalchemy import *
from sqlalchemy.orm import relationship

from api.model import Base
from ..api import DATE_TIME_FORMAT
from datetime import datetime

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120))
    email = Column(String(120))
    password_hash = Column(String(120))
    creation_time = Column(DateTime, default=lambda: datetime.utcnow())
    staff = Column(Boolean, default=False)

    characters = relationship("Character", back_populates="user")
    fleets = relationship("Fleet", back_populates="user")

    def __repr__(self):
       return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r})"

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'creation_time': self.creation_time.strftime(DATE_TIME_FORMAT),
            'staff': self.staff
        }
