import streamlit as st
from utils.styles import apply_styles
from utils.components import get_base64_image
from helpers.config import get_settings
from pymongo import MongoClient
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.vectordbFactory import VectordbFactory
from stores.llm.templates.template_parser import TemplateParser
from dataclasses import dataclass
from pymongo.database import Database
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from tools.courses_tools import list_all_courses_summaries, get_course_details
from tools.roadmaps_tools import list_all_roadmaps, get_roadmap_details
from tools.crm_tools import save_crm_ticket
from tools.semantic_search_tools import semantic_tools_list
from tools.text_search_tools import text_tools_list
from controllers.NLPController import NLPController
from typing import Optional
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.openrouter import OpenRouterModel

# Force clear cache so the new Agent initialization is picked up
st.cache_resource.clear()

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
    settings = get_settings()  # Handles both .env (local) and st.secrets (cloud)
    
    # Initialize MongoDB Client
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    
    
    # LLMFactory instance
    llm_factory = LLMFactory(settings= settings)

    # create llm generation client
    generation_client = llm_factory.create_provider_instance(provider_name = settings.GENERATION_BACKEND)
    generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # create llm embedding client
    embedding_client = llm_factory.create_provider_instance(provider_name = settings.EMBEDDING_BACKEND)
    embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID, embedding_size = settings.EMBEDDING_MODEL_SIZE)

    # create llm reranker client
    reranking_client = llm_factory.create_provider_instance(provider_name = settings.RERANKING_BACKEND)
    reranking_client.set_reranking_model(model_id = settings.RERANKING_MODEL_ID)
    
    # create vector db client
    vectordb_factory = VectordbFactory(settings= settings)
    vectordb_client = vectordb_factory.create_provider_instance(provider=settings.VECTOR_DB_BACKEND)

    # template parser
    template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG)
    
    from tools.text_search_tools import AgentDeps
    
    # toolset
    tools = [
        list_all_courses_summaries, get_course_details, 
        get_roadmap_details, list_all_roadmaps, save_crm_ticket
    ] + text_tools_list

    # provider = OpenAIProvider(
    #     base_url="https://openrouter.ai/api/v1",
    #     api_key=settings.OPENROUTER_API_KEY
    # )
    # model = OpenAIModel("google/gemini-3.1-flash-lite", provider=provider)

    model = OpenRouterModel("google/gemini-3.1-flash-lite")
    # create agent client
    agent_client = Agent(
        model = model,
        deps_type = AgentDeps,
        system_prompt = template_parser.get("rag", "system_prompt"),
        tools=tools,
        model_settings=ModelSettings(temperature=0.2)
    )

    
    return {"settings": settings, "db": db, "agent_client": agent_client, "template_parser": template_parser,
            "vectordb_client": vectordb_client, "generation_client":generation_client, "embedding_client":embedding_client,
              "reranking_client": reranking_client}

# Warm up the resources once and inject them into session state for all sub-pages
if "resources" not in st.session_state:
    st.session_state.resources = get_global_resources()

from handlers.user import login, register, get_profile
from models.enums.ResponseEnums import ResponseSignal

# ─── Simple Login ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div style="text-align: center; margin-bottom: 1rem; margin-top: 5rem;"><img src="{logo_base64}" style="height: 120px; object-fit: contain;"></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("<h2 style='text-align: center; color: #1a1d3a; font-family: Tajawal, sans-serif; margin-bottom: 2rem;'>تسجيل الدخول | Login</h2>", unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="user@kayfa.com")
                password = st.text_input("Password", type="password", placeholder="password")
                submit = st.form_submit_button("Login", type="primary", use_container_width=True)
                
                if submit:
                    res = login(st.session_state.resources["db"], {"email": email, "password": password})
                    if res.get("signal") == ResponseSignal.LOGIN_SUCCESS.value:
                        st.session_state.logged_in = True
                        st.session_state.user_id = res.get("user_id")
                        st.session_state.user_role = res.get("user_role", "user")
                        st.session_state.user_name = res.get("user_name", "User")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                        
        with tab2:
            st.markdown("<h2 style='text-align: center; color: #1a1d3a; font-family: Tajawal, sans-serif; margin-bottom: 2rem;'>إنشاء حساب | Sign Up</h2>", unsafe_allow_html=True)
            with st.form("signup_form"):
                new_name = st.text_input("Full Name", placeholder="John Doe")
                new_email = st.text_input("Email", placeholder="user@kayfa.com")
                new_password = st.text_input("Password", type="password", placeholder="password")
                new_role = st.selectbox("Role", ["user", "admin"])
                signup_submit = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
                
                if signup_submit:
                    res = register(st.session_state.resources["db"], {"name": new_name, "email": new_email, "password": new_password, "role": new_role})
                    if res.get("signal") == ResponseSignal.USER_REGISTER_SUCCESS.value:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(res.get("signal"))
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# NAVIGATION ROUTING (Must be initialized before st.page_link is called)
# ══════════════════════════════════════════════════════════════════════════════

user_role = st.session_state.get("user_role", "user")

dashboard_pages = [st.Page("pages/1_Sales_Agent.py", title="🤖 Sales Agent")]

if user_role == "admin":
    dashboard_pages.extend([
        st.Page("pages/2_CRM_Dashboard.py", title="📋 CRM Dashboard"),
        st.Page("pages/3_Upload_Knowledge_Base.py", title="📄 Upload Knowledge Base"),
        st.Page("pages/4_Admin_Dashboard.py", title="🛡️ Admin Dashboard")
    ])

pages = {
    "Dashboard": dashboard_pages
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
    
    st.page_link("pages/1_Sales_Agent.py", label="Sales Agent", icon="🤖")
    if user_role == "admin":
        st.page_link("pages/2_CRM_Dashboard.py", label="CRM Dashboard", icon="📋")
        st.page_link("pages/3_Upload_Knowledge_Base.py", label="Upload Knowledge Base", icon="📄")
        st.page_link("pages/4_Admin_Dashboard.py", label="Admin Dashboard", icon="🛡️")
    



# Render the selected page
pg.run()

with st.sidebar:
    st.markdown("---")
    if "user_id" in st.session_state:
        profile_res = get_profile(st.session_state.resources["db"], st.session_state.user_id)
        if profile_res.get("signal") == ResponseSignal.PROFILE_FOUND.value:
            user_data = profile_res.get("userData", {})
            user_name = user_data.get('user_name', 'User').strip()
            user_role = user_data.get('user_role', 'user').capitalize()
            parts = user_name.split()
            initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else user_name[:2].upper()
            
            profile_html = f"""
            <div style="display: flex; align-items: center; gap: 15px; padding: 12px; background-color: var(--secondary-background-color, #ffffff); border-radius: 12px; border: 1px solid rgba(128, 128, 128, 0.2); box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); margin-bottom: 10px;">
                <div style="min-width: 48px; min-height: 48px; border-radius: 50%; background: linear-gradient(135deg, #5e68e0, #4652d3); display: flex; justify-content: center; align-items: center; color: white; font-weight: 800; font-size: 18px; box-shadow: 0 4px 6px -1px rgba(70, 82, 211, 0.3);">
                    {initials}
                </div>
                <div style="display: flex; flex-direction: column; overflow: hidden; justify-content: center;">
                    <span style="font-weight: 700; color: var(--text-color, #1e293b); font-size: 16px; font-family: 'Syne', 'Inter', Tajawal, sans-serif; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{user_name}</span>
                    <span style="font-size: 12px; color: #64748b; font-family: 'Inter', Tajawal, sans-serif; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{user_role}</span>
                </div>
            </div>
            """
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(profile_html, unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                if st.button("🚪", key="signout_btn", help="Sign Out", use_container_width=True):
                    st.session_state["logged_in"] = False
                    if "user_id" in st.session_state:
                        del st.session_state["user_id"]
                    if "current_chat_id" in st.session_state:
                        st.session_state["current_chat_id"] = None
                    if "messages" in st.session_state:
                        st.session_state["messages"] = []
                    st.rerun()
    st.markdown("---")
    st.markdown('<div style="font-size:0.72rem;color:var(--tagline-color);">📊 Based on MongoDB Atlas data<br>for Kayfa Sales Agent.</div>',
                unsafe_allow_html=True)
