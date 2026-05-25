from pydantic import BaseModel

class ScoringRequest(BaseModel):
    place_id: str
    variables: dict
