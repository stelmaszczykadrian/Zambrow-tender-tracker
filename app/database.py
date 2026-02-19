from logging import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import DATABASE_URL, ENGINE_KWARGS
from .models import Base


class DatabaseManager:
    def __init__(self, db_url: str, engine_kwargs: dict):
        self.engine = create_engine(db_url, **engine_kwargs)
        self.session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.session_factory()


db_manager = DatabaseManager(db_url=DATABASE_URL, engine_kwargs=ENGINE_KWARGS)
