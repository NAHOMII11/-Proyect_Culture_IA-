from sqlalchemy import create_engine, Table, Column, String, DateTime, JSON, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://audit_user:audit_pass@audit_db:5432/audit_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

metadata = MetaData()

audit_events_table = Table(
    "audit_events",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("event_type", String, nullable=False),
    Column("source_service", String, nullable=False),
    Column("reference_id", String, nullable=False),
    Column("payload_summary", JSON, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

class AuditRepository:
    def create_event(self, event_data: dict) -> dict:
        with SessionLocal() as session:
            stmt = audit_events_table.insert().values(**event_data).returning(audit_events_table)
            result = session.execute(stmt)
            session.commit()
            row = result.mappings().first()
            return dict(row) if row is not None else {}

    def list_events(self, skip: int = 0, limit: int = 100) -> list:
        with SessionLocal() as session:
            stmt = audit_events_table.select().offset(skip).limit(limit).order_by(audit_events_table.c.created_at.desc())
            result = session.execute(stmt)
            return [dict(row) for row in result.mappings().all()]