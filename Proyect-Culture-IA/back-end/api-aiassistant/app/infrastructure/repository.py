from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.domain.models import ChatQuery
from uuid import UUID
from typing import Optional, Tuple, List


class ChatQueryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: str,
        query_text: str,
        response_text: Optional[str] = None,
        ai_provider: str = "openai",
        status: str = "success",
        metadata: Optional[dict] = None,
    ) -> ChatQuery:
        db_query = ChatQuery(
            user_id=user_id,
            query_text=query_text,
            response_text=response_text,
            ai_provider=ai_provider,
            status=status,
            metadata_json=metadata,
        )
        self.db.add(db_query)
        self.db.commit()
        self.db.refresh(db_query)
        return db_query

    def get_by_id(self, query_id: UUID) -> Optional[ChatQuery]:
        return self.db.query(ChatQuery).filter(ChatQuery.id == query_id).first()

    def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 10) -> Tuple[int, List[ChatQuery]]:
        query = (
            self.db.query(ChatQuery)
            .filter(ChatQuery.user_id == user_id)
            .order_by(desc(ChatQuery.created_at))
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return total, items

    def list_all(self, skip: int = 0, limit: int = 10) -> Tuple[int, List[ChatQuery]]:
        query = self.db.query(ChatQuery).order_by(desc(ChatQuery.created_at))
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return total, items

    def update(
        self,
        query_id: UUID,
        response_text: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[ChatQuery]:
        db_query = self.db.query(ChatQuery).filter(ChatQuery.id == query_id).first()
        if db_query:
            if response_text is not None:
                db_query.response_text = response_text
            if status is not None:
                db_query.status = status
            if metadata is not None:
                db_query.metadata_json = metadata
            self.db.commit()
            self.db.refresh(db_query)
        return db_query

