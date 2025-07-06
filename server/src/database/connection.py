"""
Database connection management for Bruno AI
Handle connections and sessions with the database using SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine.url import URL
import os

# Define the service class
class DatabaseManager:
    """
    Manage database connections, handle sessions, ensure connection pooling and context management.
    """

    def __init__(self, 
                 user: str = os.getenv('DB_USER', 'bruno_user'),
                 password: str = os.getenv('DB_PASSWORD', 'bruno_pass'),
                 host: str = os.getenv('DB_HOST', 'localhost'),
                 db_name: str = os.getenv('DB_NAME', 'bruno_db'),
                 database_type: str = 'postgresql'):
        """
        Initialize connection URL and engine
        :param user: Database username
        :param password: Database password
        :param host: Database hostname
        :param db_name: Database name
        :param database_type: Type of database, default to PostgreSQL
        """

        if database_type == 'postgresql':
            db_url = URL.create(
                drivername='postgresql+psycopg2',
                username=user,
                password=password,
                host=host,
                database=db_name,
                port=int(os.getenv('DB_PORT', '5432'))
            )
        else:
            db_url = URL.create(
                drivername=database_type,
                username=user,
                password=password,
                host=host,
                database=db_name
            )
        self.engine = create_engine(db_url)
        self.Base = declarative_base()
        self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def create_tables(self):
        """Create tables based on the Base metadata"""
        # Import all models to ensure they're registered with Base
        from . import models
        models.Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables based on the Base metadata"""
        self.Base.metadata.drop_all(bind=self.engine)

    def get_session(self):
        """Get the session for managing transactions"""
        return self.SessionLocal

# Global database manager instance
database_manager = DatabaseManager()
