from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.application.errors import AppError
from app.domain.entities import ConfigParameter
from app.domain.repositories import ConfigParameterRepository


class ConfigParameterService:
    def __init__(self, repo: ConfigParameterRepository):
        self._repo = repo

    def list_parameters(self) -> list[ConfigParameter]:
        return self._repo.list_all()

    def get_by_key(self, config_key: str) -> ConfigParameter:
        found = self._repo.get_by_key(config_key)
        if found is None:
            raise AppError(
                "not_found",
                f"No existe el parámetro con clave '{config_key}'.",
                [],
                status_code=404,
            )
        return found

    def get_by_id(self, parameter_id: UUID) -> ConfigParameter:
        found = self._repo.get_by_id(parameter_id)
        if found is None:
            raise AppError(
                "not_found",
                "No existe el parámetro indicado.",
                [],
                status_code=404,
            )
        return found

    def create_parameter(
        self,
        config_key: str,
        config_value: str,
        description: str | None,
    ) -> ConfigParameter:
        try:
            return self._repo.create(
                config_key=config_key.strip(),
                config_value=config_value,
                description=description,
            )
        except IntegrityError as exc:
            raise AppError(
                "conflict",
                "Ya existe un parámetro con esa clave.",
                [{"field": "config_key", "issue": "unique_violation"}],
                status_code=409,
            ) from exc

    def update_by_key(
        self,
        config_key: str,
        config_value: str | None,
        description: str | None,
    ) -> ConfigParameter:
        try:
            return self._repo.update_by_key(config_key, config_value, description)
        except KeyError as exc:
            raise AppError(
                "not_found",
                f"No existe el parámetro con clave '{config_key}'.",
                [],
                status_code=404,
            ) from exc
