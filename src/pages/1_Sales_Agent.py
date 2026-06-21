"""
Page 1 — Kayfa AI Sales Agent Chat
Customer-facing chat interface powered by a real LLM agent.
"""

import time
import streamlit as st
from utils.components import page_header, page_footer, get_base64_image, lang_toggle, t
from _agent import ConversationState, chat

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kayfa Sales Agent | وكيل مبيعات كيفا",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logo_base64 = get_base64_image("kayfa logo.svg")
page_header(logo_base64, "وكيل مبيعات كيفا | Kayfa Sales Agent")

# ─── Language toggle ──────────────────────────────────────────────────────────
lang = lang_toggle(default="ar")

# ─── Session state init ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conv_state" not in st.session_state:
    st.session_state.conv_state = ConversationState()



# ─── Welcome message (first load only) ───────────────────────────────────────
if not st.session_state.messages:
    welcome = t("chat_welcome", lang)
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    # Don't add to state.history — welcome is not part of real agent history



# ─── Clear button ─────────────────────────────────────────────────────────────
if st.button("🗑️ " + t("chat_clear", lang), key="clear_btn"):
    st.session_state.messages = []
    st.session_state.conv_state = ConversationState()
    st.rerun()

# ─── GPT-style chat CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e2e4f3;
    border-radius: 14px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 2px 8px rgba(70,82,211,0.06);
    transition: box-shadow 0.2s;
}
[data-testid="stChatMessage"]:hover {
    box-shadow: 0 4px 16px rgba(70,82,211,0.12);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #eef0ff;
    border-color: #c5caff;
}
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessageContent"] strong {
    direction: rtl;
    text-align: right;
    font-family: 'Tajawal', 'Inter', sans-serif;
    font-size: 0.97rem;
    line-height: 1.75;
    color: #1a1d3a;
}
[data-testid="stChatMessageAvatarContainer"] { align-self: flex-start; }
[data-testid="stChatInput"] {
    border-radius: 12px !important;
    border: 1.5px solid #e2e4f3 !important;
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #4652d3 !important;
    box-shadow: 0 0 0 3px rgba(70,82,211,0.12) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Render conversation history ──────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])
        if msg.get("ts"):
            st.caption(msg["ts"])

# ─── Chat input ───────────────────────────────────────────────────────────────
user_input = st.chat_input(t("chat_placeholder_ar", lang), key="chat_input")

# ─── Message processing ───────────────────────────────────────────────────────
if user_input and user_input.strip():
    ts = time.strftime("%H:%M")

    # Immediately show the user message
    st.session_state.messages.append({"role": "user", "content": user_input, "ts": ts})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
        st.caption(ts)

    # Call the real agent and stream the spinner inside the agent bubble
    with st.chat_message("assistant", avatar="🤖"):
        thinking_label = "جاري التفكير..." if lang == "ar" else "Thinking..."
        with st.spinner(thinking_label):
            reply, new_state, ticket_just_saved = chat(
                user_input,
                st.session_state.conv_state,
                lang=lang,
            )
        st.markdown(reply)
        st.caption(ts)

    # Persist results
    st.session_state.conv_state = new_state
    st.session_state.messages.append({"role": "assistant", "content": reply, "ts": ts})

    st.rerun()



page_footer(logo_base64)