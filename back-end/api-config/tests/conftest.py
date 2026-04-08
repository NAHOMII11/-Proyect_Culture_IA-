from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.domain.entities import ConfigParameter
from app.main import app
from app.routers.config import get_repository


class InMemoryConfigRepository:
    def __init__(self):
        self._by_key: dict[str, ConfigParameter] = {}
        self._by_id: dict[UUID, ConfigParameter] = {}

    def list_all(self) -> list[ConfigParameter]:
        return sorted(self._by_key.values(), key=lambda p: p.config_key)

    def get_by_key(self, config_key: str) -> ConfigParameter | None:
        return self._by_key.get(config_key)

    def get_by_id(self, parameter_id: UUID) -> ConfigParameter | None:
        return self._by_id.get(parameter_id)

    def create(
        self,
        config_key: str,
        config_value: str,
        description: str | None,
    ) -> ConfigParameter:
        if config_key in self._by_key:
            raise IntegrityError("mock", None, None)
        now = datetime.now(timezone.utc)
        pid = uuid4()
        row = ConfigParameter(
            id=pid,
            config_key=config_key,
            config_value=config_value,
            description=description,
            created_at=now,
            updated_at=now,
        )
        self._by_key[config_key] = row
        self._by_id[pid] = row
        return row

    def update_by_key(
        self,
        config_key: str,
        config_value: str | None,
        description: str | None,
    ) -> ConfigParameter:
        row = self._by_key.get(config_key)
        if row is None:
            raise KeyError(config_key)
        now = datetime.now(timezone.utc)
        updated = ConfigParameter(
            id=row.id,
            config_key=row.config_key,
            config_value=config_value if config_value is not None else row.config_value,
            description=description if description is not None else row.description,
            created_at=row.created_at,
            updated_at=now,
        )
        self._by_key[config_key] = updated
        self._by_id[row.id] = updated
        return updated


@pytest.fixture
def in_memory_repo() -> InMemoryConfigRepository:
    return InMemoryConfigRepository()


@pytest.fixture
def client(monkeypatch, in_memory_repo: InMemoryConfigRepository):
    monkeypatch.setenv("SKIP_DB_BOOTSTRAP", "1")
    app.dependency_overrides[get_repository] = lambda: in_memory_repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    monkeypatch.delenv("SKIP_DB_BOOTSTRAP", raising=False)
