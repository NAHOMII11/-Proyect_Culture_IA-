from pydantic import BaseModel


class ImportResponse(BaseModel):
    batch_id: str
    status: str
    processed_rows: int
    valid_rows: int
    invalid_rows: int


class ErrorDetail(BaseModel):
    row_number: int
    field_name: str
    error_type: str
    message: str