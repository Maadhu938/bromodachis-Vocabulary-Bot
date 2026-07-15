import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Create Base first (before importing models)
Base = declarative_base()

# Note: Models are imported in init_db() to avoid circular imports

SQLALCHEMY_DATABASE_URL = "sqlite:///./vocab.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import models here to avoid circular imports
    from app.models.vocabulary import Vocabulary
    from app.models.user import User, UserWord, QuizResult
    Base.metadata.create_all(bind=engine)
