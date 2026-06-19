from pydantic import BaseModel
from typing import Optional
from bson.objectid import ObjectId

class ChatRequest(BaseModel):
    
    user_id: Optional[str]
    is_guest: bool = False
    query: str
    limit: Optional[int] = 10

class RenameChatRequest(BaseModel):

    new_title: str
