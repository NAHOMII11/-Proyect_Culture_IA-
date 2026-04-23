from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Si existe la variable en Docker la usa, si no, usa localhost para tus pruebas locales
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin_user:cultural_password_2024@localhost:5433/places_db")

# Estos datos deben coincidir con tu docker-compose.yml
# Cambia el 5432 por 5433
# 'db_places' es el nombre del servicio en tu docker-compose
SQLALCHEMY_DATABASE_URL = "postgresql://admin_user:cultural_password_2024@db_places:5432/places_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Función para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()