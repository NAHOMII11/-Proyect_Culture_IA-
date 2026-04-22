from sqlalchemy.orm import Session
from .database import ScoreModel

class ScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_score(self, score_data: dict):
        db_score = ScoreModel(**score_data)
        # Upsert: actualiza si ya existe el place_id
        self.db.merge(db_score)
        self.db.commit()
        return db_score

    def get_by_id(self, place_id: str):
        return self.db.query(ScoreModel).filter(ScoreModel.place_id == place_id).first()

    def get_top_ranking(self, limit=10):
        return self.db.query(ScoreModel).order_by(ScoreModel.score_value.desc()).limit(limit).all()

    def update_score(self, place_id: str, score_data: dict):
        score = self.db.query(ScoreModel).filter(ScoreModel.place_id == place_id).first()
        if score:
            for key, value in score_data.items():
                setattr(score, key, value)
            self.db.commit()
            return score
        return None

    def delete_score(self, place_id: str):
        score = self.db.query(ScoreModel).filter(ScoreModel.place_id == place_id).first()
        if score:
            self.db.delete(score)
            self.db.commit()
            return True
        return False
