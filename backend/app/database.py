from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://scuser:scpassword@localhost:5432/supplychain")

# Engine = the actual connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal = a factory that creates DB sessions (like temporary workspaces)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = the parent class all our models will inherit from
Base = declarative_base()

# Dependency: gives each API request its own DB session, then closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
