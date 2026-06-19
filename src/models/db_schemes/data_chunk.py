from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias = "_id") # make the _id ObjectId data type
    chunk_text: str = Field(..., min_length = 1)        # chunk text field
    chunk_metadata: dict                                # chunk metadata field
    chunk_order: int = Field(..., gt = 0)               # chunk order field and force it to start from one
    chunk_project_id: ObjectId                          # chunk project id
    chunk_asset_id: ObjectId
    # make the pydantic accept the ObjectId type
    class Config:
        arbitrary_types_allowed = True


    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("chunk_project_id", 1)
                ],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
        ]