from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from utils.styles import apply_styles
from utils.components import get_base64_image
from helpers.config import get_settings
from pymongo import MongoClient
from stores.llm.LLMFactory import LLMFactory
from stores.llm.templates.template_parser import TemplateParser
from dataclasses import dataclass
from pymongo.database import Database
from pydantic_ai import Agent
from tools.courses_tools import list_all_courses_summaries, get_course_details
from tools.roadmaps_tools import list_all_roadmaps, get_roadmap_details
from tools.crm_tools import save_crm_ticket

# ── Page Config (must be first) ───────────────────────────────────────────────
st.set_page_config(
    page_title="Kayfa | E-Learning Dashboard v3",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply light/dark mode CSS
apply_styles()

logo_base64 = get_base64_image("kayfa logo.svg")

# --- 2. Global Resource Lifecycle Caching --------------------------------------
@st.cache_resource
def get_global_resources():
    settings = get_settings() # Grab your project settings
    
    # Initialize MongoDB Client
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    
    
    # LLMFactory instance
    llm_factory = LLMFactory(settings= settings)

    # template parser
    template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG)
    
    # deps
    @dataclass
    class AgentDeps:
        db: Database | None = None   # MongoDB database — may be None if offline

    # toolset
    toolset = [list_all_courses_summaries, get_course_details, get_roadmap_details,
               list_all_roadmaps, save_crm_ticket]

    # create agent client
    agent_client = Agent(
        model = "openrouter:google/gemini-3-flash-preview",
        deps_type = AgentDeps,
        system_prompt = template_parser.get("rag", "system_prompt"),
        toolsets=toolset
    )

    
    return {"settings": settings, "db": db, "agent_client": agent_client, "template_parser": template_parser}

# Warm up the resources once and inject them into session state for all sub-pages
if "resources" not in st.session_state:
    st.session_state.resources = get_global_resources()


# ══════════════════════════════════════════════════════════════════════════════
# NAVIGATION ROUTING (Must be initialized before st.page_link is called)
# ══════════════════════════════════════════════════════════════════════════════

pages = {
    "Dashboard": [
        st.Page("pages/1_Sales_Agent.py", title="📊 Sales Agent"),
        st.Page("pages/2_CRM_Dashboard.py", title="📈 CRM Dashboard"),
        
    ]
}

pg = st.navigation(pages, position="hidden")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR – Global Filters Shared Across st.navigation
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding: 12px 0 24px; display: flex; flex-direction: column; align-items: flex-start; gap: 10px;'>
        <img src="{logo_base64}" style="height: 65px; width: auto; object-fit: contain;" alt="Kayfa Logo">
        <div style='font-size:0.72rem;color:var(--tagline-color);letter-spacing:0.5px;'>Educational Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)    
    

    st.markdown("---")
    st.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)
    
    st.page_link("pages/1_Sales_Agent.py", label="Sales Agent", icon="📊")
    st.page_link("pages/2_CRM_Dashboard.py", label="CRM Dashboard", icon="📈")
    



# Render the selected page
pg.run()

with st.sidebar:
    st.markdown("---")
    st.markdown('<div style="font-size:0.72rem;color:var(--tagline-color);">📊 Based on MongoDB Atlas data<br>generated for Kayfa exploratory analysis.</div>',
                unsafe_allow_html=True)
