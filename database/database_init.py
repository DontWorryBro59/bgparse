from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from database.models import Base

DB_USER = os.getenv('DB_USER') or 'postgres'
DB_PASSWORD = os.getenv('DB_PASSWORD') or 'postgres'
DB_HOST = os.getenv('DB_HOST') or 'localhost'
DB_PORT = os.getenv('DB_PORT') or '5432'
DB_NAME = os.getenv('DB_NAME') or 'postgres'

db_url = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')


class DatabaseRepository:
    """
    Repository class for database operations.
    """

    def __init__(self, url):
        self._engine = create_engine(url)
        self._Session = sessionmaker(bind=self._engine)

    def create_tables(self):
        """
        Create tables in the database.
        """
        Base.metadata.create_all(self._engine)

    def drop_tables(self):
        """
        Drop tables from the database.
        """
        Base.metadata.drop_all(self._engine)

    def get_session(self):
        """
        Get a database session.
        """
        return self._Session()
