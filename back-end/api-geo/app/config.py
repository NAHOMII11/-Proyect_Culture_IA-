from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GEO_SERVICE_PORT = int(os.getenv("GEO_SERVICE_PORT", "8001"))