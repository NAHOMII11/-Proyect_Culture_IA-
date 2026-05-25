from typing import Protocol
from uuid import UUID

from app.domain.entities import ConfigParameter


class ConfigParameterRepository(Protocol):
    def list_all(self) -> list[ConfigParameter]: ...

    def get_by_key(self, config_key: str) -> ConfigParameter | None: ...

    def get_by_id(self, parameter_id: UUID) -> ConfigParameter | None: ...

    def create(
        self,
        config_key: str,
        config_value: str,
        description: str | None,
    ) -> ConfigParameter: ...

    def update_by_key(
        self,
        config_key: str,
        config_value: str | None,
        description: str | None,
    ) -> ConfigParameter: ...
