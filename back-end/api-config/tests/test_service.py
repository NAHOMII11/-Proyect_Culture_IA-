from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.application.config_parameter_service import ConfigParameterService
from app.application.errors import AppError
from tests.conftest import InMemoryConfigRepository


def test_get_by_key_not_found():
    repo = InMemoryConfigRepository()
    service = ConfigParameterService(repo)
    with pytest.raises(AppError) as exc:
        service.get_by_key("missing")
    assert exc.value.status_code == 404


def test_create_maps_integrity_to_conflict():
    repo = MagicMock()
    repo.create.side_effect = IntegrityError("stmt", {}, Exception())
    service = ConfigParameterService(repo)
    with pytest.raises(AppError) as exc:
        service.create_parameter("k", "v", None)
    assert exc.value.status_code == 409
    assert exc.value.error == "conflict"
