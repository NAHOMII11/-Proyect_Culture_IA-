import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_.]*$", re.IGNORECASE)


class ConfigParameterBase(BaseModel):
    config_key: str = Field(..., min_length=1, max_length=255)
    config_value: str = Field(..., min_length=1)
    description: str | None = Field(None, max_length=500)

    @field_validator("config_key")
    @classmethod
    def key_format(cls, v: str) -> str:
        key = v.strip()
        if not _KEY_PATTERN.match(key):
            raise ValueError(
                "config_key debe empezar con alfanumérico y solo usar letras, números, punto y guion bajo."
            )
        return key


class ConfigParameterCreate(ConfigParameterBase):
    pass


class ConfigParameterUpdate(BaseModel):
    config_value: str | None = Field(None, min_length=1)
    description: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "ConfigParameterUpdate":
        if self.config_value is None and self.description is None:
            raise ValueError("Debe enviar config_value y/o description.")
        return self


class ConfigParameterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    config_key: str
    config_value: str
    description: str | None
    created_at: datetime
    updated_at: datetime
