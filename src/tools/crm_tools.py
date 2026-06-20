from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any
from pydantic_ai import RunContext
from _mongo import save_ticket
import random
from pymongo.database import Database
from dataclasses import dataclass

# ─── Agent Dependencies ───────────────────────────────────────────────────────

@dataclass
class AgentDeps:
    db: Database | None = None   # MongoDB database — may be None if offline

# ─── CRM Ticket Model ─────────────────────────────────────────────────────────

class CRMTicket(BaseModel):
    lead_id: str = Field(
        default_factory=lambda: f"LEAD-{datetime.now().year}-{random.randint(1000,9999):04d}"
    )
    status: str = "warm"          # hot | warm | cold
    name: str = ""
    phone: str = ""
    city: str = ""
    dialect: str = ""
    interested_courses: str = ""
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

def save_crm_ticket(
    ctx: RunContext[AgentDeps],
    name: str,
    phone: str,
    city: str,
    dialect: str,
    interested_courses: str,
    goal: str,
    current_level: str,
    buy_signals: str,
    objections: str,
    conversation_summary: str,
    next_action: str,
    status: str,
) -> str:
    """
    Save a qualified lead as a CRM ticket to MongoDB.
    Call this tool when you have collected: phone + interested course (at minimum).
    All text fields MUST be in Arabic. Course names and technical terms stay in English.

    Args:
        name: اسم العميل
        phone: رقم الهاتف أو واتساب
        city: المدينة والدولة
        dialect: اللهجة (مثل: العربية — اللهجة المصرية)
        interested_courses: الدورات محل الاهتمام
        goal: الهدف من الدراسة
        current_level: المستوى الحالي (مبتدئ / متوسط / متقدم)
        buy_signals: إشارات الشراء الملاحظة
        objections: الاعتراضات إن وُجدت
        conversation_summary: ملخص المحادثة بالعربية
        next_action: الإجراء التالي المقترح
        status: تقييم العميل (hot / warm / cold)
    """
    ticket = CRMTicket(
        name=name,
        phone=phone,
        city=city,
        dialect=dialect,
        interested_courses=interested_courses,
        goal=goal,
        current_level=current_level,
        buy_signals=buy_signals,
        objections=objections,
        conversation_summary=conversation_summary,
        next_action=next_action,
        status=status,
    )
    success, msg = save_ticket(ticket.to_mongo_dict())
    # Store on ctx so the caller can detect it
    ctx.deps.__dict__["_last_ticket"] = ticket
    if success:
        return f"✅ تم حفظ تذكرة CRM بنجاح | Lead ID: {ticket.lead_id}"
    return f"⚠️ فشل الحفظ: {msg}"