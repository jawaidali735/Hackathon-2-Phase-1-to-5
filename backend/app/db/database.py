from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import QueuePool
import os
from typing import Generator
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

# Get database URL from settings
from app.core.config import settings

# Import all models to ensure they are registered with SQLModel
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message
DATABASE_URL = settings.DATABASE_URL

# Create engine with enhanced connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_timeout=30,     # Timeout for getting connection from pool
    echo=False,          # Set to True for SQL logging
)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session for FastAPI endpoints.
    Implements proper session management with exception handling.
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

# Add connection event listeners for monitoring
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Set SQLite pragmas for better performance and reliability.
    This is mainly for SQLite compatibility but won't harm other DBs.
    """
    if 'sqlite' in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")  # Enable foreign key constraints
        cursor.close()


def create_db_and_tables():
    """
    Create all database tables defined by SQLModel.
    Called during application startup.
    """
    SQLModel.metadata.create_all(engine)