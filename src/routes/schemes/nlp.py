from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    do_reset: Optional[bool]

class SearchRequest(BaseModel):
    
    query: str
    limit: Optional[int] = 3
