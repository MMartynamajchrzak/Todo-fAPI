from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:test123@localhost/ToDoFastAPIDatabase"

# create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# instance of a db session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create base, allows to create each db model
Base = declarative_base()
