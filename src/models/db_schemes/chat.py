from pydantic import Field, BaseModel
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Chat(BaseModel):
    id: Optional[ObjectId] = Field(None, alias = "_id")
    chat_project_id: ObjectId
    chat_user_id: Optional[ObjectId] = Field(None)
    is_guest_chat: bool
    chat_title: Optional[str] = Field(None)
    chat_history: list[dict]
    chat_conversation: list[dict] 
    updatedAt: datetime = Field(default_factory=datetime.utcnow),
    expiresAt: Optional[datetime] = Field(None)

    class Config():
         arbitrary_types_allowed = True
    

    @classmethod
    def get_indexes(cls):
         return [
               {
                    "key": [("chat_project_id", 1)],
                    "name": "chat_project_id_index_1",
                    "unique": False,
               },
               {
                    "key": [("expiresAt", 1)],
                    "name": "expiresAt_index_1",
                    "unique": False,
                    "expireAfterSeconds": 0
               }]