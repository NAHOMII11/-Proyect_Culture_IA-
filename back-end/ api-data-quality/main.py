import uuid
import csv
import io
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/data_quality_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la base de datos
class ImportBatchDB(Base):
    __tablename__ = "import_batches"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="processing")
    processed_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    invalid_rows = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ImportErrorDB(Base):
    __tablename__ = "import_errors"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, index=True)
    row_number = Column(Integer)
    field_name = Column(String)
    error_type = Column(String)
    message = Column(Text)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Data Quality Service")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

def validate_csv(batch_id: str, content: str, db: Session):
    # Obtener el batch de la DB
    batch = db.query(ImportBatchDB).filter(ImportBatchDB.id == batch_id).first()
    if not batch:
        
        return

    f = io.StringIO(content)
    
    try:
        sample = content[:1024]
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)
    except:
        f.seek(0)
        reader = csv.DictReader(f)
    
    if reader.fieldnames:
        reader.fieldnames = [n.strip().lower() for n in reader.fieldnames]
    
    required_columns = ["nombre", "ciudad", "direccion"]
    
    if not all(col in (reader.fieldnames or []) for col in required_columns):
        batch.status = "failed"
        db.commit()
        return

    processed = 0
    valid = 0
    invalid = 0
    errors_to_save = []

    for i, row in enumerate(reader, start=2):
        processed += 1
        row_errors = []
        
        for col in required_columns:
            val = row.get(col, "")
            if not val or not str(val).strip():
                error_entry = ImportErrorDB(
                    batch_id=batch_id,
                    row_number=i,
                    field_name=col,
                    error_type="missing_field",
                    message=f"El campo \'{col}\' es obligatorio"
                )
                row_errors.append(error_entry)
        
        if row_errors:
            invalid += 1
            errors_to_save.extend(row_errors)
        else:
            valid += 1
            
    batch.status = "completed"
    batch.processed_rows = processed
    batch.valid_rows = valid
    batch.invalid_rows = invalid
    db.add_all(errors_to_save)
    db.commit()
    db.refresh(batch)

@app.post("/imports", response_model=ImportResponse, status_code=202)
async def create_import(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")
    
    batch_id = str(uuid.uuid4())
    
    
    new_batch = ImportBatchDB(id=batch_id, status="processing")
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    raw_content = await file.read()
    try:
        content = raw_content.decode("utf-8")
    except UnicodeDecodeError:
        content = raw_content.decode("latin-1")
    
    background_tasks.add_task(validate_csv, batch_id, content, db)
    
    return ImportResponse(
        batch_id=new_batch.id,
        status=new_batch.status,
        processed_rows=new_batch.processed_rows,
        valid_rows=new_batch.valid_rows,
        invalid_rows=new_batch.invalid_rows
    )

@app.get("/imports/{batch_id}", response_model=ImportResponse)
async def get_import_status(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(ImportBatchDB).filter(ImportBatchDB.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch no encontrado")
    return ImportResponse(
        batch_id=batch.id,
        status=batch.status,
        processed_rows=batch.processed_rows,
        valid_rows=batch.valid_rows,
        invalid_rows=batch.invalid_rows
    )

@app.get("/imports/{batch_id}/errors", response_model=List[ErrorDetail])
async def get_import_errors(batch_id: str, db: Session = Depends(get_db)):
    errors = db.query(ImportErrorDB).filter(ImportErrorDB.batch_id == batch_id).all()
    if not errors and not db.query(ImportBatchDB).filter(ImportBatchDB.id == batch_id).first():
        raise HTTPException(status_code=404, detail="Batch no encontrado")
    return [
        ErrorDetail(
            row_number=err.row_number,
            field_name=err.field_name,
            error_type=err.error_type,
            message=err.message
        ) for err in errors
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
