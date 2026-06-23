from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, Session
from collections.abc import Generator

from src.database.connection import engine

# Create a session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    Guarantees session cleanup after the request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT 1")
        )

        print(
            "Database Connected:",
            result.scalar()
        )