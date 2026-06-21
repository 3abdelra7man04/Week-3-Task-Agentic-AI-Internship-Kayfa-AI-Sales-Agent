"""
_agent.py — Kayfa AI Sales Agent
Uses pydantic_ai with a real LLM (OpenRouter / Gemini Flash) and MongoDB tools.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import streamlit as st
from pydantic import BaseModel, Field
from pymongo.database import Database
from tools.crm_tools import CRMTicket
from pydantic_ai.messages import ModelMessage
from controllers.NLPController import NLPController
import traceback
from pydantic_ai.messages import ToolReturnPart, ToolCallPart, ModelResponse

def print_tools_called_with_results(result):
    print("\n=== TOOL TRACE ===\n")

    for msg in result.all_messages():
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                if isinstance(part, ToolCallPart):
                    print(f"[CALL] {part.tool_name} -> {part.args}")

                elif isinstance(part, ToolReturnPart):
                    print(f"[RETURN] {part.tool_name} -> {part.content}")
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


from tools.semantic_search_tools import AgentDeps



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
    # Build NLPController from cached resources (done here in main thread, not inside async tools)
    _resources = st.session_state.resources
    nlp_controller = NLPController(
        generation_client=_resources["generation_client"],
        embedding_client=_resources["embedding_client"],
        vectordb_client=_resources["vectordb_client"],
        template_parser=_resources["template_parser"],
        reranking_client=_resources["reranking_client"],
    )
    deps = AgentDeps(db=db, nlp_controller=nlp_controller)

    # Run the agent (with graceful error handling)
    try:
        result = agent.run_sync(
            user_message,
            deps=deps,
            message_history= state.history,
        )
        reply = result.output
        # Update history
        state.history = result.all_messages()
        print_tools_called_with_results(result)
    except ExceptionGroup as eg:
        # err_str = str(exc)
        # if "401" in err_str or "auth" in err_str.lower() or "api_key" in err_str.lower():
        #     reply = (
        #         "⚠️ خطأ في المصادقة مع نموذج الذكاء الاصطناعي.\n\n"
        #         "يرجى التحقق من صحة `OPENAI_API_KEY` في ملف `.env`.\n\n"
        #         f"_تفاصيل: {err_str[:200]}_"
        #     )
        # else:
        #     reply = (
        #         f"⚠️ حدث خطأ أثناء معالجة طلبك:\n\n_{err_str[:300]}_"
        #     )
        print(f"Caught ExceptionGroup with {len(eg.exceptions)} errors:")
        for i, exc in enumerate(eg.exceptions, 1):
            print(f"\n--- Sub-Exception {i} ---")
            traceback.print_exception(type(exc), exc, exc.__traceback__)


    # Detect if save_crm_ticket was called this turn
    ticket_just_saved = False

    return reply, state, ticket_just_saved
