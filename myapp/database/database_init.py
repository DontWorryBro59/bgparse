from myapp.database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = ('postgresql+psycopg2://postgres:1234qwerty@localhost:5432/beregDB')

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