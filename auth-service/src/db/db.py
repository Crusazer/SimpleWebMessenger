from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings

engine = create_engine(settings.DB_URL)
