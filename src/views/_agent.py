"""
_agent.py — Kayfa AI Sales Agent using pydantic_ai mock functions.

The agent:
  1. Responds naturally to customer questions about Kayfa courses.
  2. Gradually extracts lead qualification data through conversation.
  3. When enough data is collected, calls qualify_lead() tool to create
     a CRM ticket and save it to MongoDB.

All tickets are written in Arabic (course/tech names stay in English).
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel


# ─── CRM Ticket Schema ───────────────────────────────────────────────────────

class CRMTicket(BaseModel):
    lead_id: str = Field(default_factory=lambda: f"LEAD-{datetime.now().year}-{random.randint(1000,9999):04d}")
    status: str = "warm"  # hot | warm | cold
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
        d.pop("lead_id", None)
        d["lead_id"] = self.lead_id
        return d


# ─── Agent Dependencies (conversation state) ─────────────────────────────────

class ConversationState(BaseModel):
    history: list[dict[str, str]] = Field(default_factory=list)  # [{role, content}]
    extracted: dict[str, str] = Field(default_factory=dict)       # collected lead fields
    ticket_saved: bool = False
    ticket: CRMTicket | None = None


# ─── Kayfa Course Catalog (for agent knowledge) ───────────────────────────────

COURSES = {
    "SOC Track Diploma": {
        "ar_desc": "دبلومة متكاملة في الأمن السيبراني تُغطي مهارات SOC analyst من الصفر حتى الاحتراف",
        "price": "يبدأ من 2,500 ج.م",
        "duration": "6 أشهر",
        "cert": "شهادة معتمدة دولياً",
        "level": "مبتدئ → متقدم",
    },
    "Power BI for Business Analytics": {
        "ar_desc": "دورة شاملة في Power BI لتحليل البيانات وإنشاء التقارير التفاعلية — مع إعداد لشهادة PL-300",
        "price": "يبدأ من 1,800 ج.م",
        "duration": "3 أشهر",
        "cert": "شهادة Microsoft PL-300 (اختياري)",
        "level": "متوسط",
    },
    "Python Programming Bootcamp": {
        "ar_desc": "بوتكامب مكثف في Python يغطي الأساسيات حتى مشاريع حقيقية",
        "price": "يبدأ من 1,500 ج.م",
        "duration": "2 أشهر",
        "cert": "شهادة إتمام كيفا",
        "level": "مبتدئ",
    },
    "Data Science with Python": {
        "ar_desc": "مسار متكامل في علم البيانات باستخدام Python وMachine Learning",
        "price": "يبدأ من 3,000 ج.م",
        "duration": "8 أشهر",
        "cert": "شهادة إتمام كيفا",
        "level": "متوسط → متقدم",
    },
    "Linux Fundamentals": {
        "ar_desc": "أساسيات Linux للمبتدئين — المدخل الصحيح لمجالات السيبراني والسيرفرات",
        "price": "يبدأ من 800 ج.م",
        "duration": "6 أسابيع",
        "cert": "شهادة إتمام كيفا",
        "level": "مبتدئ",
    },
}


# ─── Mock Response Engine ─────────────────────────────────────────────────────

def _detect_buy_signals(text: str) -> str:
    """Detect buy signals from user message."""
    signals = []
    lower = text.lower()
    if any(w in lower for w in ["سعر", "تكلفة", "كام", "price", "cost", "تسجيل", "دفع"]):
        signals.append("سأل عن السعر وطرق الدفع")
    if any(w in lower for w in ["متى", "موعد", "when", "start", "بدء", "دفعة"]):
        signals.append("استفسر عن موعد البدء")
    if any(w in lower for w in ["شهادة", "cert", "معتمد", "اعتماد"]):
        signals.append("سأل عن الشهادة والاعتماد")
    return " — ".join(signals) if signals else ""


def _detect_objections(text: str) -> str:
    """Detect objections from user message."""
    lower = text.lower()
    if any(w in lower for w in ["غالي", "مش قادر", "مش متأكد", "فكر", "expensive", "can't"]):
        return "قلق بشأن السعر أو التوقيت"
    if any(w in lower for w in ["وقت", "مشغول", "busy", "time"]):
        return "ضغط الوقت والتزامات العمل"
    return ""


def _extract_fields(message: str, current: dict) -> dict:
    """Simple rule-based field extraction from user message."""
    extracted = dict(current)
    lower = message.lower()

    # Name detection (Arabic pattern)
    import re
    name_match = re.search(
        r"(?:اسمي|أنا|انا|my name is|i am|i'm)\s+([^\.\،,\n]{2,30})",
        message, re.IGNORECASE
    )
    if name_match and not extracted.get("name"):
        extracted["name"] = name_match.group(1).strip()

    # Phone
    phone_match = re.search(r"(\+?\d[\d\s\-]{8,15})", message)
    if phone_match and not extracted.get("phone"):
        extracted["phone"] = phone_match.group(1).strip()

    # City
    cities = {
        "القاهرة": "القاهرة، مصر", "cairo": "القاهرة، مصر",
        "الإسكندرية": "الإسكندرية، مصر", "الرياض": "الرياض، السعودية",
        "جدة": "جدة، السعودية", "دبي": "دبي، الإمارات",
        "عمّان": "عمّان، الأردن", "بغداد": "بغداد، العراق",
        "تونس": "تونس", "المغرب": "المغرب",
    }
    for city_key, city_val in cities.items():
        if city_key in message and not extracted.get("city"):
            extracted["city"] = city_val
            break

    # Courses
    for course_name in COURSES:
        if course_name.lower().split()[0].lower() in lower and not extracted.get("interested_courses"):
            extracted["interested_courses"] = course_name

    # Level
    if any(w in lower for w in ["مبتدئ", "beginner", "جديد", "لا أعرف", "صفر", "zero"]):
        extracted["current_level"] = "مبتدئ"
    elif any(w in lower for w in ["متوسط", "intermediate", "شوية", "بعض"]):
        extracted["current_level"] = "متوسط"
    elif any(w in lower for w in ["متقدم", "advanced", "محترف", "خبير"]):
        extracted["current_level"] = "متقدم"

    # Buy signals
    sig = _detect_buy_signals(message)
    if sig:
        existing = extracted.get("buy_signals", "")
        extracted["buy_signals"] = (existing + " — " + sig).strip(" — ") if existing else sig

    # Objections
    obj = _detect_objections(message)
    if obj:
        extracted["objections"] = obj

    return extracted


def _score_lead(extracted: dict) -> str:
    """Score lead quality based on collected fields."""
    score = 0
    if extracted.get("name"):       score += 2
    if extracted.get("phone"):      score += 3
    if extracted.get("city"):       score += 1
    if extracted.get("interested_courses"): score += 2
    if extracted.get("goal"):       score += 1
    if extracted.get("buy_signals"): score += 3
    if score >= 8:  return "hot"
    if score >= 4:  return "warm"
    return "cold"


def _build_arabic_response(user_msg: str, state: ConversationState, lang: str) -> str:
    """Generate a contextual response in the chosen language."""
    lower = user_msg.lower()
    extracted = state.extracted
    msg_count = len(state.history)

    # ── Greetings ────────────────────────────────────────────────
    if any(w in lower for w in ["مرحبا", "اهلا", "هلا", "hello", "hi", "سلام"]):
        if lang == "ar":
            return (
                "أهلاً وسهلاً! 😊\n\n"
                "أنا وكيل مبيعات كيفا، وأنا هنا لمساعدتك في اختيار المسار المناسب لك.\n\n"
                "قبل أن نبدأ، ممكن تعرّفني على نفسك؟ وما هو المجال الذي يستهويك؟"
            )
        else:
            return (
                "Hello! 😊\n\n"
                "I'm Kayfa's AI sales agent. I'm here to help you pick the right learning path.\n\n"
                "Could you tell me a bit about yourself and what field interests you most?"
            )

    # ── Course inquiries ─────────────────────────────────────────
    if "soc" in lower or "سيبراني" in lower or "cybersec" in lower or "أمن" in lower:
        if lang == "ar":
            return (
                "ممتاز! مجال الأمن السيبراني من أكثر المجالات طلباً الآن. 🔐\n\n"
                "**SOC Track Diploma** من كيفا هو مسارنا الأشمل في هذا المجال:\n"
                f"- 📚 **المدة:** {COURSES['SOC Track Diploma']['duration']}\n"
                f"- 💰 **السعر:** {COURSES['SOC Track Diploma']['price']}\n"
                f"- 🏆 **الشهادة:** {COURSES['SOC Track Diploma']['cert']}\n"
                f"- 📊 **المستوى:** {COURSES['SOC Track Diploma']['level']}\n\n"
                "ما هو مستواك الحالي في الشبكات أو الأمن؟ وما هدفك من الدراسة؟"
            )
        else:
            return (
                "Great choice! Cybersecurity is one of the most in-demand fields right now. 🔐\n\n"
                "Our **SOC Track Diploma** is our most comprehensive cybersecurity program:\n"
                f"- 📚 **Duration:** {COURSES['SOC Track Diploma']['duration']}\n"
                f"- 💰 **Price:** {COURSES['SOC Track Diploma']['price']}\n"
                f"- 🏆 **Certificate:** {COURSES['SOC Track Diploma']['cert']}\n\n"
                "What's your current level, and what's your goal?"
            )

    if "power bi" in lower or "بيانات" in lower or "data" in lower or "تحليل" in lower:
        if lang == "ar":
            return (
                "رائع! تحليل البيانات مجال في نمو مستمر. 📊\n\n"
                "عندنا مسارين مناسبين:\n"
                f"1. **Power BI for Business Analytics** — {COURSES['Power BI for Business Analytics']['ar_desc']}\n"
                f"   💰 {COURSES['Power BI for Business Analytics']['price']} | ⏱ {COURSES['Power BI for Business Analytics']['duration']}\n\n"
                f"2. **Data Science with Python** — {COURSES['Data Science with Python']['ar_desc']}\n"
                f"   💰 {COURSES['Data Science with Python']['price']} | ⏱ {COURSES['Data Science with Python']['duration']}\n\n"
                "هل لديك خلفية في Excel أو SQL؟ وما هدفك المهني؟"
            )
        else:
            return (
                "Excellent! Data analytics is a booming field. 📊\n\n"
                "We have two great paths:\n"
                "1. **Power BI for Business Analytics** — Covers interactive dashboards & PL-300 prep\n"
                "2. **Data Science with Python** — Full ML & data science track\n\n"
                "Do you have any Excel or SQL background? What's your career goal?"
            )

    if "python" in lower or "برمجة" in lower or "programming" in lower:
        if lang == "ar":
            return (
                "Python اختيار ممتاز للبدء! 🐍\n\n"
                f"**Python Programming Bootcamp** من كيفا:\n"
                f"- 📚 المدة: {COURSES['Python Programming Bootcamp']['duration']}\n"
                f"- 💰 السعر: {COURSES['Python Programming Bootcamp']['price']}\n"
                f"- 🎯 المستوى: {COURSES['Python Programming Bootcamp']['level']}\n\n"
                "هل تريد تعلم Python للعمل في تطوير التطبيقات أم تحليل البيانات أم مجال آخر؟"
            )
        else:
            return (
                "Python is a great starting point! 🐍\n\n"
                f"Our **Python Programming Bootcamp**: {COURSES['Python Programming Bootcamp']['duration']} | {COURSES['Python Programming Bootcamp']['price']}\n\n"
                "Are you learning Python for app development, data analysis, or something else?"
            )

    # ── Pricing questions ─────────────────────────────────────────
    if any(w in lower for w in ["سعر", "تكلفة", "كام", "price", "cost", "غالي", "قسط", "installment"]):
        if lang == "ar":
            return (
                "بالطبع! نحن في كيفا نقدم أسعاراً تنافسية مع خيارات دفع مرنة. 💳\n\n"
                "معظم دوراتنا متاحة بـ **التقسيط** براتب شهري مناسب.\n\n"
                "لكي أقدر أوفرلك العرض الأنسب، ممكن تخبرني:\n"
                "1. اسمك ورقم تواصلك\n"
                "2. الدورة اللي تفكر فيها\n\n"
                "وسيتواصل معك أحد مندوبينا بعروض خاصة! 🎯"
            )
        else:
            return (
                "Of course! Kayfa offers competitive pricing with flexible installment options. 💳\n\n"
                "To give you the best offer, could you share:\n"
                "1. Your name and contact number\n"
                "2. Which course you're interested in\n\n"
                "Our team will reach out with a personalized offer! 🎯"
            )

    # ── Contact info provided ─────────────────────────────────────
    import re
    phone_in_msg = re.search(r"(\+?\d[\d\s\-]{8,15})", user_msg)
    if phone_in_msg:
        if lang == "ar":
            return (
                "شكراً جزيلاً على ثقتك! ✅\n\n"
                "تم تسجيل بياناتك وسيتواصل معك أحد مندوبي المبيعات في كيفا خلال **24 ساعة** عبر واتساب.\n\n"
                "هل هناك أي استفسار آخر يمكنني مساعدتك به؟ 😊"
            )
        else:
            return (
                "Thank you! ✅\n\n"
                "Your details have been registered. A Kayfa sales rep will contact you within **24 hours** via WhatsApp.\n\n"
                "Is there anything else I can help you with? 😊"
            )

    # ── Goal / motivation ─────────────────────────────────────────
    if any(w in lower for w in ["هدف", "goal", "شغل", "وظيفة", "job", "عمل", "مستقبل", "احتراف"]):
        if lang == "ar":
            return (
                "هدف رائع! 🚀\n\n"
                "كيفا صممت مساراتها خصيصاً للتحول المهني السريع مع **شهادات معتمدة** تُفرق في سوق العمل.\n\n"
                "لكي أساعدك بشكل أدق، أخبرني:\n"
                "- ما مستواك الحالي؟ (مبتدئ / متوسط / متقدم)\n"
                "- هل تعمل حالياً أم طالب؟"
            )
        else:
            return (
                "Great goal! 🚀\n\n"
                "Kayfa's tracks are designed for fast career transitions with **industry-recognized certificates**.\n\n"
                "To advise you better:\n"
                "- What's your current level? (Beginner / Intermediate / Advanced)\n"
                "- Are you currently working or a student?"
            )

    # ── Catch-all after several messages — ask for contact ────────
    if msg_count >= 4 and not extracted.get("phone"):
        if lang == "ar":
            return (
                "يسعدني أنني أقدر أساعدك! 😊\n\n"
                "لنُكمل الحديث بشكل أفضل ويتواصل معك متخصصنا، ممكن تشاركني:\n"
                "- **اسمك الكريم**\n"
                "- **رقم الواتساب** للتواصل\n\n"
                "سيتواصل معك أحد مندوبي المبيعات لتقديم عرض مخصص لك 🎯"
            )
        else:
            return (
                "I'm happy to help! 😊\n\n"
                "To connect you with our specialist, could you share:\n"
                "- **Your name**\n"
                "- **WhatsApp number**\n\n"
                "Our rep will reach out with a personalized offer! 🎯"
            )

    # ── Generic helpful response ──────────────────────────────────
    if lang == "ar":
        return (
            "شكراً على سؤالك! 😊\n\n"
            "كيفا تقدم مجموعة متنوعة من المسارات التدريبية في:\n"
            "• الأمن السيبراني (SOC Track Diploma)\n"
            "• تحليل البيانات (Power BI، Data Science)\n"
            "• البرمجة (Python Bootcamp)\n"
            "• أساسيات Linux\n\n"
            "أيٌّ من هذه المجالات يستهويك؟ أو هل لديك مجال آخر في بالك؟ 🤔"
        )
    else:
        return (
            "Thanks for your question! 😊\n\n"
            "Kayfa offers a variety of training tracks:\n"
            "• Cybersecurity (SOC Track Diploma)\n"
            "• Data Analytics (Power BI, Data Science)\n"
            "• Programming (Python Bootcamp)\n"
            "• Linux Fundamentals\n\n"
            "Which area interests you most? 🤔"
        )


def _build_ticket(state: ConversationState) -> CRMTicket:
    """Build a CRM ticket from extracted conversation data."""
    ext = state.extracted
    history = state.history

    # Auto-generate conversation summary
    user_messages = [h["content"] for h in history if h["role"] == "user"]
    summary_parts = []
    if ext.get("interested_courses"):
        summary_parts.append(f"مهتم بـ {ext['interested_courses']}")
    if ext.get("goal"):
        summary_parts.append(f"هدفه: {ext['goal']}")
    if ext.get("current_level"):
        summary_parts.append(f"مستواه {ext['current_level']}")
    if ext.get("buy_signals"):
        summary_parts.append(ext["buy_signals"])
    if not summary_parts:
        summary_parts.append("تفاعل مع الوكيل واستفسر عن دورات كيفا")

    summary = "عميل تحدث مع الوكيل الذكي. " + "، ".join(summary_parts) + "."

    # Auto-generate next action
    status = _score_lead(ext)
    if status == "hot":
        next_action = "يتواصل مندوب المبيعات خلال 24 ساعة عبر واتساب لتأكيد التسجيل"
    elif status == "warm":
        next_action = "إرسال بروشور المسار المناسب عبر البريد أو واتساب ومتابعة خلال 48 ساعة"
    else:
        next_action = "إضافته لقائمة المتابعة الشهرية وإرسال محتوى تعليمي مجاني"

    # Detect dialect from city
    city = ext.get("city", "")
    if "مصر" in city or "القاهرة" in city or "الإسكندرية" in city:
        dialect = "العربية — اللهجة المصرية"
    elif "السعودية" in city or "الرياض" in city or "جدة" in city:
        dialect = "العربية — اللهجة الخليجية (السعودية)"
    elif "الإمارات" in city or "دبي" in city:
        dialect = "العربية — اللهجة الإماراتية"
    elif "الأردن" in city or "عمّان" in city:
        dialect = "العربية — اللهجة الأردنية"
    else:
        dialect = ext.get("dialect", "العربية")

    return CRMTicket(
        status=status,
        name=ext.get("name", "غير مُدخل"),
        phone=ext.get("phone", "غير مُدخل"),
        city=ext.get("city", "غير مُدخلة"),
        dialect=dialect,
        interested_courses=ext.get("interested_courses", "غير محدد"),
        goal=ext.get("goal", "غير مُدخل"),
        current_level=ext.get("current_level", "غير محدد"),
        buy_signals=ext.get("buy_signals", "لا توجد إشارات واضحة"),
        objections=ext.get("objections", "لا توجد اعتراضات مسجّلة"),
        conversation_summary=summary,
        next_action=next_action,
    )


# ─── pydantic_ai Agent Setup ─────────────────────────────────────────────────

# We use TestModel so no real API key is needed — pure mock behaviour
_test_model = TestModel()

agent = Agent(
    model=_test_model,
    system_prompt=(
        "أنت وكيل مبيعات ذكي لشركة كيفا للتدريب التقني. "
        "ساعد العملاء في اختيار المسار المناسب وجمع بياناتهم بشكل طبيعي."
    ),
)


@agent.tool_plain
def qualify_lead(
    name: str,
    phone: str,
    interested_courses: str,
) -> str:
    """Called when the agent has enough data to qualify a lead."""
    return f"تم تسجيل العميل {name} بنجاح — دورة: {interested_courses} — رقم: {phone}"


# ─── Public chat function ─────────────────────────────────────────────────────

def chat(user_message: str, state: ConversationState, lang: str = "ar") -> tuple[str, ConversationState, bool]:
    """
    Process a user message and return (agent_reply, updated_state, ticket_just_saved).

    The agent uses mock functions (no real LLM required).
    Returns ticket_just_saved=True the first time a ticket is written.
    """
    # Add user message to history
    state.history.append({"role": "user", "content": user_message})

    # Extract fields from user message
    state.extracted = _extract_fields(user_message, state.extracted)

    # Generate contextual response
    reply = _build_arabic_response(user_message, state, lang)

    # Add assistant response to history
    state.history.append({"role": "assistant", "content": reply})

    # ── Decide whether to save ticket ────────────────────────────
    ticket_saved_now = False
    should_qualify = (
        not state.ticket_saved
        and (
            state.extracted.get("phone")
            or (len(state.history) >= 8 and state.extracted.get("interested_courses"))
        )
    )

    if should_qualify:
        ticket = _build_ticket(state)
        state.ticket = ticket
        state.ticket_saved = True
        ticket_saved_now = True

        # Save to MongoDB (import with path guard)
        import sys, importlib, pathlib as _pl
        _views = str(_pl.Path(__file__).parent)
        if _views not in sys.path:
            sys.path.insert(0, _views)
        _mongo = importlib.import_module("_mongo")
        _mongo.save_ticket(ticket.to_mongo_dict())

    return reply, state, ticket_saved_now
