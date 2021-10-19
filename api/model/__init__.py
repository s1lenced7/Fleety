from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker

_DB_USERNAME = 'debug_user'
_DB_PASSWORD = 'debug_user'
_DB_ADDRESS = '127.0.0.1'
_DB_URI = f"mysql+pymysql://{_DB_USERNAME}:{_DB_PASSWORD}@{_DB_ADDRESS}/fleety2"

engine = create_engine(_DB_URI)
mapper_registry = registry()
Base = mapper_registry.generate_base()
Session = sessionmaker(engine)

from .user import User
from .character import Character
from .system import System
from .universe import UniverseItem
from .client_token import ClientToken
from .fleet import Fleet, FleetParticipation

mapper_registry.metadata.create_all(engine)


