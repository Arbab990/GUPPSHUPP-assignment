# backend/models.py
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True)
    kind = Column(String(64), nullable=False)   # e.g., preference, emotional_pattern, fact
    content = Column(Text, nullable=False)
    meta_json = Column(Text, nullable=True)     # renamed field (was "metadata") to avoid SQLAlchemy conflict

def init_db(db_url="sqlite:///memories.db"):
    """
    Returns a sessionmaker bound to the engine.
    """
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


