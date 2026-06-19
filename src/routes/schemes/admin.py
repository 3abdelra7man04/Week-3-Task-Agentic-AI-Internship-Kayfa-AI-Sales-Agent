from pydantic import BaseModel
from typing import Optional
from bson.objectid import ObjectId

class AdminInviteRequest(BaseModel):
    
    admin_name: str
    admin_email: str
    admin_role: str
    
