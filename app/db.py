from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

# create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

# instance of a db session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create base, allows to create each db model
Base = declarative_base()
