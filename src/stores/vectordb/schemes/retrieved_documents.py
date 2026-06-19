from pydantic import BaseModel

class RetrievedDocuments(BaseModel):
    text: str
    score: float
