from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Disable verbose SQL logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI.
    
    Usage:
        @app.get("/items")
        async def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Call this on application startup to ensure all tables exist.
    """
    # Import all models to register them with Base
    from app import models  # noqa: F401
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all database tables.
    WARNING: This will delete all data. Use only in development/testing.
    """
    from app import models  # noqa: F401
    
    Base.metadata.drop_all(bind=engine)
