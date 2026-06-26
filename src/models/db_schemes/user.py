from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class User(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_name: str
    user_email: EmailStr
    user_password: str
    user_role: str = Field(default="user")
    user_image: Optional[str] = ""


    class Config():
         arbitrary_types_allowed = True
    

    @classmethod
    def get_indexes(cls):
         return [
               {
                         "key": [("user_project_id", 1)],
                         "name": "user_project_id_index_1",
                         "unique": False
               },
               {
                    "key": [("user_email", 1)],
                    "name": "user_email_index_1",
                    "unique": True
               }]
    