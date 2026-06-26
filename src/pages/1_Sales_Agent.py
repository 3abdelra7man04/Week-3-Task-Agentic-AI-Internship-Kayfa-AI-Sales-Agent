"""
Page 1 — Kayfa AI Sales Agent Chat
Customer-facing chat interface powered by a real LLM agent.
"""

import time
import streamlit as st
from utils.components import page_header, page_footer, get_base64_image, lang_toggle, t
from _agent import ConversationState, chat
from handlers.chat import create_chat, update_chat, list_chats, get_chat, delete_chat, rename_chat
from pydantic import TypeAdapter
from pydantic_ai.messages import ModelMessage

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kayfa Sales Agent | وكيل مبيعات كيفا",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logo_base64 = get_base64_image("kayfa logo.svg")
page_header(logo_base64, "وكيل مبيعات كيف | Kayfa Sales Agent")

st.title("🤖 Kayfa Sales Agent")

# ─── Language toggle ──────────────────────────────────────────────────────────
lang = lang_toggle(default="ar")

# ─── Session state init ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conv_state" not in st.session_state:
    st.session_state.conv_state = ConversationState()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

db_client = st.session_state.resources["db"]
user_id = st.session_state.get("user_id", None)

# ─── Sidebar Chat History ─────────────────────────────────────────────────────
with st.sidebar:
    st.title("💬 سجل المحادثات" if lang == "ar" else "💬 Chat History")
    
    if st.button("➕ محادثة جديدة" if lang == "ar" else "➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conv_state = ConversationState()
        st.session_state.current_chat_id = None
        st.rerun()
    
    st.divider()
    
    if user_id:
        past_chats = list_chats(db_client, user_id)
        for c in past_chats:
            c_id = c["_id"]
            c_title = c.get("chat_title") or "New Chat"
            
            with st.expander(c_title, expanded=False):
                if st.button("فتح" if lang == "ar" else "Load", key=f"load_{c_id}", use_container_width=True):
                    st.session_state.current_chat_id = c_id
                    chat_data = get_chat(db_client, c_id)
                    if chat_data:
                        parsed_history = TypeAdapter(list[ModelMessage]).validate_python(chat_data.chat_history)
                        st.session_state.conv_state = ConversationState(history=parsed_history)
                        st.session_state.messages = []
                        for msg in chat_data.chat_conversation:
                            st.session_state.messages.append({"role": "user", "content": msg["question"], "ts": ""})
                            st.session_state.messages.append({"role": "assistant", "content": msg["answer"], "ts": ""})
                        st.rerun()
                
                new_title = st.text_input("تغيير الاسم" if lang == "ar" else "Rename", key=f"rename_input_{c_id}")
                if st.button("حفظ" if lang == "ar" else "Save", key=f"rename_btn_{c_id}"):
                    if new_title.strip():
                        rename_chat(db_client, c_id, new_title.strip())
                        st.rerun()
                
                if st.button("حذف" if lang == "ar" else "Delete", key=f"delete_{c_id}"):
                    delete_chat(db_client, c_id)
                    if st.session_state.current_chat_id == c_id:
                        st.session_state.current_chat_id = None
                        st.session_state.messages = []
                        st.session_state.conv_state = ConversationState()
                    st.rerun()
    else:
        st.info("قم بتسجيل الدخول لرؤية سجل محادثاتك" if lang == "ar" else "Log in to see your chat history.")

# ─── GPT-style chat CSS ───────────────────────────────────────────────────────
css_direction = "rtl" if lang == "ar" else "ltr"
css_text_align = "right" if lang == "ar" else "left"

st.markdown(f"""
<style>
[data-testid="stChatMessage"] {{
    background: #ffffff;
    border: 1px solid #e2e4f3;
    border-radius: 14px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 2px 8px rgba(70,82,211,0.06);
    transition: box-shadow 0.2s;
    direction: {css_direction};
}}
[data-testid="stChatMessage"]:hover {{
    box-shadow: 0 4px 16px rgba(70,82,211,0.12);
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    background: #eef0ff;
    border-color: #c5caff;
}}
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessageContent"] strong,
[data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessageContent"] h3,
[data-testid="stChatMessageContent"] h4,
[data-testid="stChatMessageContent"] h5,
[data-testid="stChatMessageContent"] h6,
[data-testid="stChatMessageContent"] span,
[data-testid="stChatMessageContent"] a {{
    text-align: {css_text_align};
    font-family: 'Tajawal', 'Inter', sans-serif;
    font-size: 0.97rem;
    line-height: 1.75;
    color: #1a1d3a !important;
}}
[data-testid="stChatMessageContent"] code {{
    color: #d83b6f !important;
    background-color: #f1f3f8 !important;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
}}
[data-testid="stChatMessageAvatarContainer"] {{ align-self: flex-start; }}
[data-testid="stChatInput"] {{
    border-radius: 12px !important;
    border: 1.5px solid #e2e4f3 !important;
    font-family: 'Tajawal', sans-serif !important;
    direction: {css_direction} !important;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: #4652d3 !important;
    box-shadow: 0 0 0 3px rgba(70,82,211,0.12) !important;
}}
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

    # Save to MongoDB
    chat_history = TypeAdapter(list).dump_python(new_state.history, mode='json')
    if st.session_state.current_chat_id is None:
        title = user_input[:30]
        c_id = create_chat(db_client, user_id, title, chat_history, [{"question": user_input, "answer": reply}])
        st.session_state.current_chat_id = c_id
    else:
        update_chat(db_client, st.session_state.current_chat_id, chat_history, user_input, reply)

    st.rerun()



page_footer(logo_base64)