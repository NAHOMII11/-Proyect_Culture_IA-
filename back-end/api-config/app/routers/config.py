from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.config_parameter_service import ConfigParameterService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.config_parameter_repository import (
    SqlAlchemyConfigParameterRepository,
)
from app.schemas.config import ConfigParameterCreate, ConfigParameterRead, ConfigParameterUpdate

router = APIRouter(tags=["config"])


def get_repository(
    db: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyConfigParameterRepository:
    return SqlAlchemyConfigParameterRepository(db)


def get_config_service(
    repo: Annotated[SqlAlchemyConfigParameterRepository, Depends(get_repository)],
) -> ConfigParameterService:
    return ConfigParameterService(repo)


@router.get("/parameters", response_model=list[ConfigParameterRead])
def list_parameters(
    service: Annotated[ConfigParameterService, Depends(get_config_service)],
) -> list[ConfigParameterRead]:
    return [ConfigParameterRead.model_validate(p) for p in service.list_parameters()]


@router.get("/parameters/by-id/{parameter_id}", response_model=ConfigParameterRead)
def get_parameter_by_id(
    parameter_id: UUID,
    service: Annotated[ConfigParameterService, Depends(get_config_service)],
) -> ConfigParameterRead:
    return ConfigParameterRead.model_validate(service.get_by_id(parameter_id))


@router.get("/parameters/by-key/{config_key:path}", response_model=ConfigParameterRead)
def get_parameter_by_key(
    config_key: str,
    service: Annotated[ConfigParameterService, Depends(get_config_service)],
) -> ConfigParameterRead:
    return ConfigParameterRead.model_validate(service.get_by_key(config_key))


@router.post("/parameters", response_model=ConfigParameterRead, status_code=201)
def create_parameter(
    body: ConfigParameterCreate,
    service: Annotated[ConfigParameterService, Depends(get_config_service)],
) -> ConfigParameterRead:
    created = service.create_parameter(
        config_key=body.config_key,
        config_value=body.config_value,
        description=body.description,
    )
    return ConfigParameterRead.model_validate(created)


@router.put("/parameters/by-key/{config_key:path}", response_model=ConfigParameterRead)
def update_parameter(
    config_key: str,
    body: ConfigParameterUpdate,
    service: Annotated[ConfigParameterService, Depends(get_config_service)],
) -> ConfigParameterRead:
    updated = service.update_by_key(
        config_key=config_key,
        config_value=body.config_value,
        description=body.description,
    )
    return ConfigParameterRead.model_validate(updated)
