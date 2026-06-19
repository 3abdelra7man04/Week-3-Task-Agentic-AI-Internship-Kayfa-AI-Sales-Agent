import streamlit as st
import pandas as pd
from utils.mongo import load_all_data, get_latest_state, save_dashboard_state, apply_filters
from utils.styles import apply_styles
from utils.components import get_base64_image

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
