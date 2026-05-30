from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = None
SessionLocal = None
Base = declarative_base()


def get_engine():
    global engine
    if engine is None:
        connect_args = {}
        if settings.DATABASE_URL.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
    return engine


def get_session_local():
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal


def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=get_engine())


def reset_engine():
    global engine, SessionLocal
    engine = None
    SessionLocal = None
