from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias = "_id") # make the _id ObjectId data type
    asset_name: str = Field(..., min_length=1) # asset text field
    asset_content: str = Field(...)

    # make the pydantic accept the ObjectId type
    class Config:
        arbitrary_types_allowed = True