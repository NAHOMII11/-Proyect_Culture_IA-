import os
from sqlalchemy import create_engine, Column, String, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# Prioriza la variable de entorno de Docker, si no, usa SQLite local para pruebas r�pidas
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./analytics_db.db')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ScoreModel(Base):
    __tablename__ = 'scores'
    __table_args__ = {'extend_existing': True}

    place_id = Column(String, primary_key=True, index=True)
    score_value = Column(Float)
    level = Column(String)
    explanation = Column(String)

Base.metadata.create_all(bind=engine)
