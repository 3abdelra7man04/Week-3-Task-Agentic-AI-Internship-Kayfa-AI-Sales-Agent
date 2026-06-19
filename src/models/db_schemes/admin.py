from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Admin(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    admin_project_id: ObjectId
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    admin_image: Optional[str] = ""
    admin_role: str
    admin_status: str
    admin_last_login: Optional[datetime] = None


    class Config():
         arbitrary_types_allowed = True
    

    @classmethod
    def get_indexes(cls):
         return [
               {
                    "key": [("admin_email", 1)],
                    "name": "admin_email_index_1",
                    "unique": True
               }]
