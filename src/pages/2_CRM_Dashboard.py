"""
Page 2 — Kayfa CRM Lead Dashboard (Sales Rep View)
Displays CRM tickets from MongoDB; falls back to mock data when DB is unavailable.
"""

import sys
import pathlib
from datetime import datetime
import streamlit as st

from utils.components import page_header, page_footer, get_base64_image, lang_toggle, t

from _mock_data import MOCK_TICKETS
from _mongo import get_tickets, is_connected

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
        "interested_courses": "المنتجات محل الاهتمام",
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
        "interested_courses": "Interested Courses",
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
    "interested_courses", "goal", "current_level",
    "buy_signals", "objections",
    "conversation_summary", "next_action", "created_at",
]


# ─── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_tickets(status_filter: str, course_filter: str) -> tuple[list[dict], bool]:
    """Load tickets from MongoDB or fall back to mocks."""
    connected = is_connected()
    if connected:
        tickets = get_tickets(
            status=status_filter if status_filter != "all" else None,
            course_keyword=course_filter if course_filter else None,
        )
        if tickets:
            return tickets, True
    # Fallback: mocks
    tickets = list(MOCK_TICKETS)
    # Apply filters to mocks
    if status_filter and status_filter != "all":
        tickets = [t for t in tickets if t.get("status") == status_filter]
    if course_filter:
        tickets = [t for t in tickets if course_filter.lower() in t.get("interested_courses", "").lower()]
    return tickets, False


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
<div class="crm-card">
  <div class="crm-card-header">
    <span class="lead-id">{lead_id}</span>
    <span class="status-badge {badge_class}">{icon} {status_label} · {'عميل محتمل' if lang=='ar' else 'Lead'}</span>
  </div>
  <div class="crm-card-body">
"""

    for field in DISPLAY_FIELDS:
        val = ticket.get(field, "")
        if not val:
            continue
        if isinstance(val, datetime):
            val = val.strftime("%Y-%m-%d · %H:%M")
        label_text = labels.get(field, field)
        extra_class = "crm-value-summary" if field in ("conversation_summary", "next_action") else "crm-value"
        html += f"""
    <div class="crm-row">
      <div class="crm-label">{label_text}</div>
      <div class="{extra_class}">{val}</div>
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
    # Two-column grid on wide screens
    col_a, col_b = st.columns(2, gap="medium")
    for i, ticket in enumerate(tickets):
        target_col = col_a if i % 2 == 0 else col_b
        with target_col:
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