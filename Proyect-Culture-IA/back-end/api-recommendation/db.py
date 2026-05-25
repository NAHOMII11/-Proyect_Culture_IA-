import os

from sqlalchemy import Column, Float, JSON, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://rec_user:rec_password@db-recommendation:5432/recommendation_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class HistoricalRecommendation(Base):
    __tablename__ = "historical_recommendations"
    id = Column(String, primary_key=True)
    place_id = Column(String, index=True)
    user_preference = Column(String)
    relevance_index = Column(Float)
    explanation = Column(JSON)


Base.metadata.create_all(bind=engine)
