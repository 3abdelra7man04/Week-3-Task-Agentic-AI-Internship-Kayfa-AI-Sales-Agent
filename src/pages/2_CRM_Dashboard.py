"""
Page 2 — Kayfa CRM Lead Dashboard (Sales Rep View)
Displays CRM tickets from MongoDB; falls back to mock data when DB is unavailable.
"""

import sys
import pathlib
from datetime import datetime
import streamlit as st

from utils.components import page_header, page_footer, get_base64_image, lang_toggle, t


logo_base64 = get_base64_image("kayfa logo.svg")

page_header(logo_base64, "CRM Dashboard")

# ── Path setup ────────────────────────────────────────────────────────────────
_views_dir = pathlib.Path(__file__).parent.parent
if str(_views_dir) not in sys.path:
    sys.path.insert(0, str(_views_dir))



# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kayfa CRM Dashboard | لوحة العملاء",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Language & styles ────────────────────────────────────────────────────────
lang = lang_toggle(default="ar")

is_rtl = lang == "ar"
direction = "rtl" if is_rtl else "ltr"
text_align = "right" if is_rtl else "left"

# ─── Status config ────────────────────────────────────────────────────────────
STATUS_CONFIG = {
    "hot":  {"ar": "ساخن",  "en": "Hot",  "class": "status-hot",  "icon": "🔴"},
    "warm": {"ar": "دافئ",  "en": "Warm", "class": "status-warm", "icon": "🟡"},
    "cold": {"ar": "بارد",  "en": "Cold", "class": "status-cold", "icon": "🔵"},
}

FIELD_LABELS = {
    "ar": {
        "name":               "الاسم",
        "phone":              "رقم التواصل",
        "city":               "المدينة",
        "dialect":            "اللغة / اللهجة",
        "interested_products": "المنتجات محل الاهتمام",
        "goal":               "الهدف",
        "current_level":      "المستوى الحالي",
        "buy_signals":        "إشارات الشراء",
        "objections":         "الاعتراضات",
        "conversation_summary": "ملخص المحادثة",
        "next_action":        "الإجراء التالي",
        "created_at":         "التاريخ",
    },
    "en": {
        "name":               "Name",
        "phone":              "Contact",
        "city":               "City",
        "dialect":            "Language / Dialect",
        "interested_products": "Interested Courses",
        "goal":               "Goal",
        "current_level":      "Current Level",
        "buy_signals":        "Buy Signals",
        "objections":         "Objections",
        "conversation_summary": "Conversation Summary",
        "next_action":        "Next Action",
        "created_at":         "Date",
    },
}

DISPLAY_FIELDS = [
    "name", "phone", "city", "dialect",
    "interested_products", "goal", "current_level",
    "buy_signals", "objections",
    "conversation_summary", "next_action", "created_at",
]


# ─── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_tickets(status_filter: str, course_filter: str) -> tuple[list[dict], bool]:
    """Load tickets from MongoDB or fall back to mocks."""
    
    # Get db connection from session state (pass it via st.session_state outside cache if possible, but accessing resources directly is ok for demo)
    resources = st.session_state.resources
    db = resources["db"]
    
    if db is not None:
        try:
            from models.CRMTicketsModel import CRMTicketsModel
            model = CRMTicketsModel(db_client=db)
            tickets_objs = model.get_all_tickets()
            tickets = [t.model_dump() for t in tickets_objs]
            # Apply filters manually since model.get_all_tickets() gets all
            if status_filter and status_filter != "all":
                tickets = [t for t in tickets if t.get("status") == status_filter]
            if course_filter:
                tickets = [t for t in tickets if course_filter.lower() in t.get("interested_products", "").lower()]
            return tickets, True
        except Exception as e:
            print(e)
            
        
    # Apply filters to mocks
    if status_filter and status_filter != "all":
        tickets = [t for t in tickets if t.get("status") == status_filter]
    if course_filter:
        tickets = [t for t in tickets if course_filter.lower() in t.get("interested_products", t.get("interested_courses", "")).lower()]
    return tickets, False


# ─── Filters ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters" if lang == "en" else "التصفية")
    chosen_status = st.selectbox(
        "Status" if lang == "en" else "الحالة",
        ["all", "hot", "warm", "cold"]
    )
    course_filter = st.text_input("Course" if lang == "en" else "الدورة", value="")

# ─── Load data ────────────────────────────────────────────────────────────────
tickets, from_db = load_tickets(chosen_status, course_filter)

# ─── Metrics row ─────────────────────────────────────────────────────────────
all_tickets, _ = load_tickets("all", "")
hot_count  = sum(1 for t in all_tickets if t.get("status") == "hot")
warm_count = sum(1 for t in all_tickets if t.get("status") == "warm")
cold_count = sum(1 for t in all_tickets if t.get("status") == "cold")

m_labels = (
    ["إجمالي العملاء", "ساخن 🔴", "دافئ 🟡", "بارد 🔵"]
    if lang == "ar"
    else ["Total Leads", "Hot 🔴", "Warm 🟡", "Cold 🔵"]
)
m_values = [len(all_tickets), hot_count, warm_count, cold_count]

cols = st.columns(4)
for col, label, val in zip(cols, m_labels, m_values):
    with col:
        st.metric(label=label, value=val)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Mock data notice ──────────────────────────────────────────────────────────
if not from_db:
    notice = (
        "⚠️ قاعدة البيانات غير متاحة — يتم عرض بيانات تجريبية للتوضيح."
        if lang == "ar"
        else "⚠️ Database unavailable — showing mock data for demonstration."
    )
    st.info(notice)

st.divider()

# ─── Ticket card renderer ─────────────────────────────────────────────────────
def render_ticket(ticket: dict, lang: str) -> str:
    status = ticket.get("status", "warm")
    cfg = STATUS_CONFIG.get(status, STATUS_CONFIG["warm"])
    status_label = cfg["ar"] if lang == "ar" else cfg["en"]
    badge_class = cfg["class"]
    icon = cfg["icon"]

    lead_id = ticket.get("lead_id", "LEAD-XXXX")
    labels = FIELD_LABELS[lang]

    # Header
    html = f"""
<div class="ticket-container">
  <div class="ticket-header">
    <span class="ticket-status">{status_label} · {'عميل محتمل' if lang=='ar' else 'Lead'}</span>
    <span class="ticket-lead-id" style="direction: ltr;">{lead_id}</span>
  </div>
  <div class="ticket-body">
"""

    for field in DISPLAY_FIELDS:
        val = ticket.get(field, "")
        if not val:
            continue
        if isinstance(val, datetime):
            val = val.strftime("%Y-%m-%d · %H:%M")
        label_text = labels.get(field, field)
        html += f"""
<div class="ticket-row">
  <div class="ticket-label">{label_text}</div>
  <div class="ticket-value">{val}</div>
</div>"""

    html += "\n  </div>\n</div>"
    return html


# ─── Render tickets ───────────────────────────────────────────────────────────
if not tickets:
    st.markdown(
        f'<p style="text-align:center;color:#8890b5;font-size:1rem;padding:2rem 0;">'
        f'{t("crm_no_tickets", lang)}</p>',
        unsafe_allow_html=True,
    )
else:
    # Inject CSS for the modern ticket UI
    st.markdown("""
    <style>
    .ticket-container {
        border: 1px solid #eaebf2;
        border-radius: 12px;
        background: #ffffff;
        margin-bottom: 24px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        direction: rtl;
    }
    .ticket-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .ticket-lead-id {
        background: #eef0ff;
        color: #4652d3;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-family: monospace;
        letter-spacing: 0.5px;
    }
    .ticket-status {
        background: #fff0e5;
        color: #c95126;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .ticket-row {
        display: flex;
        padding: 14px 16px;
        border-bottom: 1px solid #f4f5f8;
    }
    .ticket-row:nth-child(even) {
        background-color: #fbfbfc;
    }
    .ticket-row:last-child {
        border-bottom: none;
    }
    .ticket-label {
        flex: 0 0 160px;
        color: #4652d3;
        font-weight: 700;
        font-size: 0.95rem;
        padding-left: 16px;
    }
    .ticket-value {
        flex: 1;
        color: #33395c;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    # Full-width single column layout
    for ticket in tickets:
        st.markdown(render_ticket(ticket, lang), unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div style="text-align:center;color:#8890b5;font-size:0.78rem;padding:2rem 0 0.5rem;
     direction:{direction};">
    {'كيفا للتدريب التقني — لوحة إدارة العملاء المحتملين © 2026'
     if lang=='ar' else
     'Kayfa Tech Training — CRM Lead Dashboard © 2026'}
</div>
""",
    unsafe_allow_html=True,
)

page_footer(logo_base64)