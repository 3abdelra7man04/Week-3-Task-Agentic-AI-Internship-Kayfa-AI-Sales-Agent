from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Optional
from bson.objectid import ObjectId
import random

class CRMTicket(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    lead_id: str = Field(
        default_factory=lambda: f"LEAD-{datetime.now().year}-{random.randint(1000,9999):04d}"
    )
    status: str = "warm"          # hot | warm | cold
    name: str = ""
    phone: str = ""
    city: str = ""
    dialect: str = ""
    interested_products: str = ""
    goal: str = ""
    current_level: str = ""
    buy_signals: str = ""
    objections: str = ""
    conversation_summary: str = ""
    next_action: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    source: str = "chat"

    def to_mongo_dict(self) -> dict[str, Any]:
        d = self.model_dump()
        d["lead_id"] = self.lead_id
        return d