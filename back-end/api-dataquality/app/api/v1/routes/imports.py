from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.imports import ErrorDetail, ImportResponse
from app.services.import_service import ImportService
from app.workers.import_worker import validate_csv

router = APIRouter(tags=["imports"])


@router.post("/imports", response_model=ImportResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_import(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")

    batch = ImportService.create_batch(db)

    raw_content = await file.read()
    try:
        content = raw_content.decode("utf-8")
    except UnicodeDecodeError:
        content = raw_content.decode("latin-1")

    background_tasks.add_task(validate_csv, batch.id, content)

    return ImportResponse(
        batch_id=batch.id,
        status=batch.status,
        processed_rows=batch.processed_rows,
        valid_rows=batch.valid_rows,
        invalid_rows=batch.invalid_rows,
    )


@router.get("/imports/{batch_id}", response_model=ImportResponse)
def get_import_status(batch_id: str, db: Session = Depends(get_db)):
    batch = ImportService.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch no encontrado")

    return ImportResponse(
        batch_id=batch.id,
        status=batch.status,
        processed_rows=batch.processed_rows,
        valid_rows=batch.valid_rows,
        invalid_rows=batch.invalid_rows,
    )


@router.get("/imports/{batch_id}/errors", response_model=List[ErrorDetail])
def get_import_errors(batch_id: str, db: Session = Depends(get_db)):
    batch = ImportService.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch no encontrado")

    errors = ImportService.get_errors(db, batch_id)
    return [
        ErrorDetail(
            row_number=err.row_number,
            field_name=err.field_name,
            error_type=err.error_type,
            message=err.message,
        )
        for err in errors
    ]