from pydantic import Field
from pydantic_ai import RunContext
from pymongo.database import Database
from dataclasses import dataclass
from models.db_schemes import CRMTicket
from models.CRMTicketsModel import CRMTicketsModel
from datetime import datetime

# ─── Agent Dependencies ───────────────────────────────────────────────────────

@dataclass
class AgentDeps:
    db: Database | None = None   # MongoDB database — may be None if offline
    lead_id: str | None = None

def save_crm_ticket(
    ctx: RunContext[AgentDeps],
    name: str,
    phone: str,
    city: str,
    dialect: str,
    interested_products: str,
    goal: str,
    current_level: str,
    buy_signals: str,
    objections: str,
    conversation_summary: str,
    next_action: str,
    status: str,
    created_at: datetime = datetime.now(),
) -> str:
    """
    Save a qualified lead as a CRM ticket to MongoDB.
    Call this tool when you have collected: phone + interested course (at minimum).
    All text fields MUST be in Arabic. Course names and technical terms stay in English.

    Args:
        name: اسم العميل
        phone: رقم الهاتف أو واتساب
        city: المدينة والدولة
        dialect: اللهجة التي يتحدث بها العميل (سواء كانت الإنجليزية، أو لهجة عربية محددة مثل اللهجة المصرية أو غيرها)
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
        lead_id=ctx.deps.lead_id,
        name=name,
        phone=phone,
        city=city,
        dialect=dialect,
        interested_products=interested_products,
        goal=goal,
        current_level=current_level,
        buy_signals=buy_signals,
        objections=objections,
        conversation_summary=conversation_summary,
        next_action=next_action,
        status=status,
        created_at=datetime.now(),
    )
    if ctx.deps.db is None:
        return "⚠️ فشل الحفظ: قاعدة البيانات غير متصلة"
        
    try:
        model = CRMTicketsModel(db_client=ctx.deps.db)
        model.save_ticket(ticket)
        success = True
        msg = ""
    except Exception as e:
        success = False
        msg = str(e)

    # Store on ctx so the caller can detect it
    ctx.deps.__dict__["_last_ticket"] = ticket
    if success:
        return f"✅ تم حفظ تذكرة CRM بنجاح | Lead ID: {ticket.lead_id}"
    return f"⚠️ فشل الحفظ: {msg}"