from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ConfigParameter:
    id: UUID
    config_key: str
    config_value: str
    description: str | None
    created_at: datetime
    updated_at: datetime
