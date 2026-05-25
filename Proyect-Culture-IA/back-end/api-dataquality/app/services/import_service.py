import uuid
from sqlalchemy.orm import Session
from app.models.import_batch import ImportBatchDB, ImportErrorDB


class ImportService:
    @staticmethod
    def create_batch(db: Session) -> ImportBatchDB:
        batch = ImportBatchDB(id=str(uuid.uuid4()), status="processing")
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch

    @staticmethod
    def get_batch(db: Session, batch_id: str):
        return db.query(ImportBatchDB).filter(ImportBatchDB.id == batch_id).first()

    @staticmethod
    def get_errors(db: Session, batch_id: str):
        return db.query(ImportErrorDB).filter(ImportErrorDB.batch_id == batch_id).all()