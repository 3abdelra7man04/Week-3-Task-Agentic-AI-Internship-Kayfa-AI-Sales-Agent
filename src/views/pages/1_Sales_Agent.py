"""
Page 1 — Kayfa AI Sales Agent Chat
Customer-facing chat interface with bilingual support (Arabic priority).
"""

import sys
import pathlib
import time
import streamlit as st
from utils.components import page_header, page_footer, get_base64_image

logo_base64 = get_base64_image("kayfa logo.svg")

page_header(logo_base64, "Academic Overview Dashboard")

# ── Path setup so helpers are importable ─────────────────────────────────────
_views_dir = pathlib.Path(__file__).parent.parent
if str(_views_dir) not in sys.path:
    sys.path.insert(0, str(_views_dir))

from _style import lang_toggle, t
from _agent import ConversationState, chat

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kayfa Sales Agent | وكيل مبيعات كيفا",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Language toggle ──────────────────────────────────────────────────────────
lang = lang_toggle(default="ar")


# ─── Session state init ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conv_state" not in st.session_state:
    st.session_state.conv_state = ConversationState()

if "ticket_notified" not in st.session_state:
    st.session_state.ticket_notified = False

# ─── Welcome message ──────────────────────────────────────────────────────────
if not st.session_state.messages:
    welcome = t("chat_welcome", lang)
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    st.session_state.conv_state.history.append({"role": "assistant", "content": welcome})


# ─── Ticket saved banner ──────────────────────────────────────────────────────
if st.session_state.conv_state.ticket_saved and not st.session_state.ticket_notified:
    st.markdown(
        f'<div class="lead-captured-toast">{t("ticket_saved", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.session_state.ticket_notified = True


# ─── Chat message renderer ────────────────────────────────────────────────────
def render_messages():
    is_rtl = lang == "ar"
    chat_html = '<div class="chat-container">'

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"].replace("\n", "<br>")
        timestamp = msg.get("ts", "")

        if role == "user":
            chat_html += f"""
<div class="bubble-user">{content}
  <div class="chat-meta">{timestamp}</div>
</div>"""
        else:
            avatar = "🤖 "
            chat_html += f"""
<div class="bubble-agent"><span style="font-size:1.1rem;">{avatar}</span>{content}
  <div class="chat-meta">{timestamp}</div>
</div>"""

    chat_html += "</div>"
    return chat_html


# ─── Chat display area ────────────────────────────────────────────────────────
chat_area = st.container()
with chat_area:
    st.markdown(render_messages(), unsafe_allow_html=True)


# ─── Input area ───────────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

col_input, col_btn = st.columns([8, 1.5])

with col_input:
    user_input = st.text_input(
        label="",
        placeholder=t("chat_placeholder_ar", lang),
        key="chat_input",
        label_visibility="collapsed",
    )

with col_btn:
    send_clicked = st.button(t("chat_send", lang), key="send_btn", use_container_width=True)


# ─── Message processing ───────────────────────────────────────────────────────
if (send_clicked or (user_input and user_input != st.session_state.get("_last_input", ""))) and user_input.strip():
    st.session_state["_last_input"] = user_input

    # Record timestamp
    ts = time.strftime("%H:%M")

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input, "ts": ts})

    # Typing indicator placeholder
    with st.spinner("" if lang == "ar" else ""):
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            """
<div class="chat-container">
  <div class="typing-indicator">
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        time.sleep(0.8)  # simulate thinking

    # Get agent reply
    reply, new_state, ticket_just_saved = chat(
        user_input,
        st.session_state.conv_state,
        lang=lang,
    )

    # Update state
    st.session_state.conv_state = new_state
    st.session_state.messages.append({"role": "assistant", "content": reply, "ts": ts})

    if ticket_just_saved:
        st.session_state.ticket_notified = False  # show banner on next render

    typing_placeholder.empty()
    st.rerun()


# ─── Extracted data preview (collapsible) ─────────────────────────────────────
state = st.session_state.conv_state
if state.extracted:
    label = "📋 البيانات المجمّعة" if lang == "ar" else "📋 Collected Data"
    with st.expander(label, expanded=False):
        field_labels = {
            "name": "الاسم" if lang == "ar" else "Name",
            "phone": "رقم التواصل" if lang == "ar" else "Phone",
            "city": "المدينة" if lang == "ar" else "City",
            "interested_courses": "الدورة المحل اهتمام" if lang == "ar" else "Interested Courses",
            "goal": "الهدف" if lang == "ar" else "Goal",
            "current_level": "المستوى" if lang == "ar" else "Level",
            "buy_signals": "إشارات الشراء" if lang == "ar" else "Buy Signals",
            "objections": "الاعتراضات" if lang == "ar" else "Objections",
        }
        rows = ""
        for key, label_text in field_labels.items():
            val = state.extracted.get(key, "—")
            rows += f"""
<div class="crm-row">
  <div class="crm-label">{label_text}</div>
  <div class="crm-value">{val}</div>
</div>"""
        st.markdown(f'<div class="crm-card"><div class="crm-card-body">{rows}</div></div>', unsafe_allow_html=True)

page_footer(logo_base64)