import os
from abc import ABC, abstractmethod
from functools import lru_cache
from uuid import UUID

from sqlalchemy import Column, DateTime, Index, MetaData, String, Table, create_engine, func, select
from sqlalchemy.dialects.postgresql import JSON, UUID as PGUUID
from sqlalchemy.orm import sessionmaker

from app.domain.audit_event import AuditEvent, AuditEventFilter

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://audit_user:audit_pass@audit_db:5432/audit_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()
SessionLocal = sessionmaker(bind=engine)


def init_tables() -> None:
    metadata.create_all(bind=engine)

audit_events_table = Table(
    "audit_events",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column("event_type", String(120), nullable=False),
    Column("source_service", String(120), nullable=False),
    Column("reference_id", String(255), nullable=False),
    Column("payload_summary", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_audit_events_created_at", "created_at"),
    Index("ix_audit_events_event_type", "event_type"),
    Index("ix_audit_events_source_service", "source_service"),
    Index("ix_audit_events_reference_id", "reference_id"),
)


class AuditRepository(ABC):
    """Puerto de persistencia (Dependency Inversion)."""

    @abstractmethod
    def create(self, event: AuditEvent) -> AuditEvent:
        pass

    @abstractmethod
    def list_by_filter(self, filters: AuditEventFilter) -> list[AuditEvent]:
        pass

    @abstractmethod
    def get_by_id(self, event_id: UUID) -> AuditEvent | None:
        pass

    @abstractmethod
    def count_by_filter(self, filters: AuditEventFilter) -> int:
        pass

    @abstractmethod
    def summary_by_field(self, field_name: str, filters: AuditEventFilter) -> dict[str, int]:
        pass


class PostgresAuditRepository(AuditRepository):
    def _apply_filters(self, stmt, filters: AuditEventFilter):
        if filters.event_type:
            stmt = stmt.where(audit_events_table.c.event_type == filters.event_type)
        if filters.source_service:
            stmt = stmt.where(audit_events_table.c.source_service == filters.source_service)
        if filters.reference_id:
            stmt = stmt.where(audit_events_table.c.reference_id == filters.reference_id)
        if filters.date_from:
            stmt = stmt.where(audit_events_table.c.created_at >= filters.date_from)
        if filters.date_to:
            stmt = stmt.where(audit_events_table.c.created_at <= filters.date_to)
        return stmt

    def _row_to_entity(self, row) -> AuditEvent:
        return AuditEvent(
            id=row["id"],
            event_type=row["event_type"],
            source_service=row["source_service"],
            reference_id=row["reference_id"],
            payload_summary=row["payload_summary"] or {},
            created_at=row["created_at"],
        )

    def create(self, event: AuditEvent) -> AuditEvent:
        with SessionLocal() as session:
            stmt = (
                audit_events_table.insert()
                .values(
                    id=event.id,
                    event_type=event.event_type,
                    source_service=event.source_service,
                    reference_id=event.reference_id,
                    payload_summary=event.payload_summary,
                    created_at=event.created_at,
                )
                .returning(audit_events_table)
            )
            result = session.execute(stmt)
            session.commit()
            row = result.mappings().first()
            return self._row_to_entity(row)

    def list_by_filter(self, filters: AuditEventFilter) -> list[AuditEvent]:
        stmt = select(audit_events_table)
        stmt = self._apply_filters(stmt, filters)
        stmt = (
            stmt.order_by(audit_events_table.c.created_at.desc())
            .offset(filters.skip)
            .limit(filters.limit)
        )
        with SessionLocal() as session:
            rows = session.execute(stmt).mappings().all()
            return [self._row_to_entity(row) for row in rows]

    def get_by_id(self, event_id: UUID) -> AuditEvent | None:
        stmt = select(audit_events_table).where(audit_events_table.c.id == event_id)
        with SessionLocal() as session:
            row = session.execute(stmt).mappings().first()
            return self._row_to_entity(row) if row else None

    def count_by_filter(self, filters: AuditEventFilter) -> int:
        stmt = select(func.count()).select_from(audit_events_table)
        stmt = self._apply_filters(stmt, filters)
        with SessionLocal() as session:
            return int(session.execute(stmt).scalar_one())

    def summary_by_field(self, field_name: str, filters: AuditEventFilter) -> dict[str, int]:
        column = audit_events_table.c[field_name]
        stmt = select(column, func.count().label("total")).select_from(audit_events_table)
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.group_by(column).order_by(func.count().desc())
        with SessionLocal() as session:
            rows = session.execute(stmt).all()
            return {str(row[0]): int(row[1]) for row in rows if row[0] is not None}


@lru_cache
def get_audit_repository() -> AuditRepository:
    return PostgresAuditRepository()
