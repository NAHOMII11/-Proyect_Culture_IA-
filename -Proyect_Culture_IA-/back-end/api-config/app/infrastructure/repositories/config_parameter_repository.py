from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities import ConfigParameter
from app.infrastructure.models import ConfigParameterORM


def _to_entity(row: ConfigParameterORM) -> ConfigParameter:
    return ConfigParameter(
        id=row.id,
        config_key=row.config_key,
        config_value=row.config_value,
        description=row.description,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SqlAlchemyConfigParameterRepository:
    def __init__(self, session: Session):
        self._session = session

    def list_all(self) -> list[ConfigParameter]:
        rows = self._session.query(ConfigParameterORM).order_by(ConfigParameterORM.config_key).all()
        return [_to_entity(r) for r in rows]

    def get_by_key(self, config_key: str) -> ConfigParameter | None:
        row = (
            self._session.query(ConfigParameterORM)
            .filter(ConfigParameterORM.config_key == config_key)
            .one_or_none()
        )
        return _to_entity(row) if row else None

    def get_by_id(self, parameter_id: UUID) -> ConfigParameter | None:
        row = self._session.get(ConfigParameterORM, parameter_id)
        return _to_entity(row) if row else None

    def create(
        self,
        config_key: str,
        config_value: str,
        description: str | None,
    ) -> ConfigParameter:
        now = datetime.now(timezone.utc)
        row = ConfigParameterORM(
            config_key=config_key.strip(),
            config_value=config_value,
            description=description,
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise
        self._session.refresh(row)
        return _to_entity(row)

    def update_by_key(
        self,
        config_key: str,
        config_value: str | None,
        description: str | None,
    ) -> ConfigParameter:
        row = (
            self._session.query(ConfigParameterORM)
            .filter(ConfigParameterORM.config_key == config_key)
            .one_or_none()
        )
        if row is None:
            raise KeyError(config_key)
        if config_value is not None:
            row.config_value = config_value
        if description is not None:
            row.description = description
        row.updated_at = datetime.now(timezone.utc)
        self._session.commit()
        self._session.refresh(row)
        return _to_entity(row)
