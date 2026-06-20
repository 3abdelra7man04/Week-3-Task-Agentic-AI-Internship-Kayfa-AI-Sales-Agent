"""
_agent.py — Kayfa AI Sales Agent
Uses pydantic_ai with a real LLM (OpenRouter / Gemini Flash) and MongoDB tools.
"""

from __future__ import annotations
from dataclasses import dataclass
import streamlit as st
from pydantic import BaseModel, Field
from pymongo.database import Database
from tools.crm_tools import CRMTicket
from pydantic_ai.messages import ModelMessage


# ─── resources ──────────────────────────────────────
resources = st.session_state.resources
settings = resources["settings"]
db = resources["db"]
agent = resources["agent_client"]
template_parser = resources["template_parser"]



# ─── Conversation state (passed in/out of the chat() function) ───────────────
class ConversationState(BaseModel):
    history: list[ModelMessage] = Field(default_factory=list)
    ticket_saved: bool = False
    ticket: CRMTicket | None = None


# ─── Agent Dependencies ───────────────────────────────────────────────────────
@dataclass
class AgentDeps:
    db: Database | None = None   # MongoDB database — may be None if offline



# ─── Public chat() function ───────────────────────────────────────────────────
def chat(
    user_message: str,
    state: ConversationState,
    lang: str = "ar",
) -> tuple[str, ConversationState, bool]:
    """
    Send a message to the agent and return (reply, updated_state, ticket_just_saved).

    Uses agent.run_sync() with the full conversation history as message_history.
    """
    deps = AgentDeps(db=db)

    # Run the agent (with graceful error handling)
    try:
        result = agent.run_sync(
            user_message,
            deps=deps,
            message_history= state.history,
        )
        reply = result.output
    except Exception as exc:
        err_str = str(exc)
        if "401" in err_str or "auth" in err_str.lower() or "api_key" in err_str.lower():
            reply = (
                "⚠️ خطأ في المصادقة مع نموذج الذكاء الاصطناعي.\n\n"
                "يرجى التحقق من صحة `OPENAI_API_KEY` في ملف `.env`.\n\n"
                f"_تفاصيل: {err_str[:200]}_"
            )
        else:
            reply = (
                f"⚠️ حدث خطأ أثناء معالجة طلبك:\n\n_{err_str[:300]}_"
            )

    # Update history
    state.history = result.all_messages()

    # Detect if save_crm_ticket was called this turn
    ticket_just_saved = False

    return reply, state, ticket_just_saved
