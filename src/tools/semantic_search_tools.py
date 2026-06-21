# semantic_search_tools.py
# One search tool per knowledge-base file in data/text/.
# Each tool calls NLPController.search_in_vectordb with:
#   collection_id = "Kayfa_Sales_Agent_" + <file stem>
#   limit = 2
#
# NLPController is received via ctx.deps.nlp_controller (injected by _agent.py
# in the main thread before agent.run_sync is called) to avoid accessing
# st.session_state inside pydantic_ai's async TaskGroup context.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from pymongo.database import Database
from pydantic_ai import RunContext
from controllers.NLPController import NLPController


# ── Dependency type (mirrors AgentDeps in _agent.py) ─────────────────────────
@dataclass
class AgentDeps:
    db: Database | None = None
    nlp_controller: Optional[NLPController] = None
    lead_id: str | None = None


def _format_results(results) -> str:
    """Convert reranked document dicts into a readable string."""
    if not results:
        return "No relevant information found."
    lines = []
    for i, doc in enumerate(results, start=1):
        text = doc.get("text", doc) if isinstance(doc, dict) else str(doc)
        lines.append(f"[{i}] {text}")
    return "\n\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Kayfa_Fullstack_Diploma
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_fullstack_diploma(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa Full-Stack Diploma knowledge base for information relevant
    to the user's query. Use this tool when the user asks about the Full-Stack
    web-development diploma offered by Kayfa (curriculum, pricing, duration,
    prerequisites, instructors, etc.).

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_Kayfa_Fullstack_Diploma",
            query=query,
            limit=2,
        )
        print(f"Retrieved documents: {results}")
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve Full-Stack Diploma information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Kayfa_PenTest_Diploma
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_pentest_diploma(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa Penetration-Testing Diploma knowledge base. Use this tool
    when the user asks about the Pen-Test / Ethical Hacking diploma (modules,
    certifications, fees, schedule, etc.).

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_Kayfa_PenTest_Diploma",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve PenTest Diploma information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. kayfa_ai_diploma
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_ai_diploma(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa AI Diploma knowledge base. Use this tool when the user
    asks about the Artificial-Intelligence diploma program (tracks, tools,
    projects, pricing, etc.).

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_ai_diploma",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve AI Diploma information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. kayfa_company_overview
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_company_overview(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa company-overview knowledge base. Use this tool when the
    user asks general questions about Kayfa as a company (mission, vision,
    history, contact info, locations etc.).

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_company_overview",
            query=query,
            limit=2,
        )
        print(f"Retrieved documents: {results}")
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve company overview information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 5. kayfa_data_science_diploma
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_data_science_diploma(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa Data-Science Diploma knowledge base. Use this tool when
    the user asks about the Data Science diploma (curriculum, tools, projects,
    pricing, etc.).

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_data_science_diploma",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve Data Science Diploma information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 6. kayfa_free_educational_content
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_free_educational_content(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa free educational-content knowledge base. Use this tool
    when the user asks about free resources, videos, articles, or courses
    available at no cost on the Kayfa platform.

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_free_educational_content",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve free educational content information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 7. kayfa_instructor_network
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_instructor_network(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa instructor-network knowledge base. Use this tool when the
    user asks about Kayfa's instructors, how to become an instructor, teaching
    partnerships, or instructor profiles.

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_instructor_network",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve instructor network information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 8. kayfa_paid_educational_tracks
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_paid_educational_tracks(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa paid educational-tracks knowledge base. Use this tool
    when the user asks about structured paid learning tracks (bundles, paths,
    subscriptions, pricing, etc.).

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_paid_educational_tracks",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve paid educational tracks information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 9. kayfa_paid_individual_courses
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_paid_individual_courses(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa paid individual-courses knowledge base. Use this tool
    when the user asks about specific standalone paid courses (topics, prices,
    duration, instructors, etc.).

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_paid_individual_courses",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve paid individual courses information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 10. kayfa_policies_and_faqs
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_policies_and_faqs(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa policies-and-FAQs knowledge base. Use this tool when the
    user asks about refund policies, enrollment rules, certificates, terms of
    service, or any frequently asked questions.

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_policies_and_faqs",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve policies and FAQs information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 11. kayfa_privacy_policy
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_privacy_policy(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa privacy-policy knowledge base. Use this tool when the
    user asks about data privacy, GDPR compliance, personal data usage, or
    Kayfa's privacy practices.

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_privacy_policy",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve privacy policy information: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 12. kayfa_soc_diploma
# ─────────────────────────────────────────────────────────────────────────────
def search_kayfa_soc_diploma(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the Kayfa SOC (Security Operations Center) Diploma knowledge base.
    Use this tool when the user asks about the SOC diploma program (modules,
    certifications, career path, pricing, etc.).

    Args:
        query: The user's question or search phrase. MUST BE IN ENGLISH. Always translate the user's Arabic query to English before searching!
    """
    try:
        nlp: NLPController = ctx.deps.nlp_controller
        results, _, _ = nlp.search_in_vectordb(
            collection_id="Kayfa_Sales_Agent_kayfa_soc_diploma",
            query=query,
            limit=2,
        )
        return _format_results(results)
    except Exception as e:
        return f"Could not retrieve SOC Diploma information: {e}"

# ─── Exported Tools List ──────────────────────────────────────────────────────
semantic_tools_list = [
    search_kayfa_fullstack_diploma,
    search_kayfa_pentest_diploma,
    search_kayfa_ai_diploma,
    search_kayfa_company_overview,
    search_kayfa_data_science_diploma,
    search_kayfa_free_educational_content,
    search_kayfa_instructor_network,
    search_kayfa_paid_educational_tracks,
    search_kayfa_paid_individual_courses,
    search_kayfa_policies_and_faqs,
    search_kayfa_privacy_policy,
    search_kayfa_soc_diploma,
]
