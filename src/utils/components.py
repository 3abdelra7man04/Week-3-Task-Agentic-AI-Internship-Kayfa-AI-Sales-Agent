import streamlit as st
import os
import base64

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            if os.path.exists(image_path + ext):
                image_path = image_path + ext
                break
    try:
        with open(image_path, "rb") as img_file:
            mime_type = "image/svg+xml" if image_path.lower().endswith(".svg") else "image/png"
            return f"data:{mime_type};base64,{base64.b64encode(img_file.read()).decode()}"
    except FileNotFoundError:
        return ""

def kpi(col, label, value, delta_html, accent):
    col.markdown(f"""
    <div class="kpi-card kpi-accent-{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div>{delta_html}</div>
    </div>
    """, unsafe_allow_html=True)

def page_header(logo_b64, subtitle):
    st.markdown(f"""
    <div class="kayfa-header" style="padding: 32px 36px;">
        <div style="display: flex; align-items: center; gap: 24px;">
            <img src="{logo_b64}" style="height: 95px; width: auto; object-fit: contain;" alt="Kayfa Logo">
            <div style="border-left: 1px solid var(--sidebar-border); padding-left: 24px;">
                <div class="kayfa-tagline" style="font-size: 1.25rem; color: var(--text-color); font-weight: 600; margin-bottom: 4px;">Week #3 Task - Part 1</div>
                <div style="font-size: 0.85rem; color: var(--tagline-color); font-weight: 300; letter-spacing: 0.3px;">{subtitle}</div>
            </div>
        </div>
        <div style="flex:1"></div>
        <div style="text-align:right">
            <div style="font-size:0.72rem;color:var(--tagline-color);">Last Updated</div>
            <div style="font-size:0.88rem;color:var(--text-color);font-weight:500;">June 2026</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def page_footer(logo_b64):
    st.markdown(f"""
    <div style="text-align:center;padding:25px 0 12px;color:var(--tagline-color);font-size:0.75rem; display:flex; align-items:center; justify-content:center; gap:10px;">
        <img src="{logo_b64}" style="height: 24px; width: auto; object-fit: contain;" alt="Kayfa Logo">
        <span>· Week #3 Task - Part 1 · © 2026 Kayfa Inc.</span>
    </div>
    """, unsafe_allow_html=True)

def lang_toggle(default: str = "ar") -> str:
    """Render a language toggle and return 'ar' or 'en'."""
    if "lang" not in st.session_state:
        st.session_state["lang"] = default

    col1, col2 = st.columns([8, 2])
    with col2:
        options = ["🇸🇦 العربية", "🇬🇧 English"]
        idx = 0 if st.session_state["lang"] == "ar" else 1
        chosen = st.selectbox(
            label="Language",
            options=options,
            index=idx,
            key="lang_select",
            label_visibility="collapsed",
        )
        st.session_state["lang"] = "ar" if "العربية" in chosen else "en"

    return st.session_state["lang"]


# ─── i18n strings ────────────────────────────────────────────────────────────
I18N: dict[str, dict[str, str]] = {
    # Page 1 — Chat
    "chat_placeholder_ar": {
        "ar": "اكتب رسالتك هنا...",
        "en": "Type your message here...",
    },
    "chat_send": {"ar": "إرسال", "en": "Send"},
    "chat_clear": {"ar": "مسح المحادثة", "en": "Clear chat"},
    "chat_welcome": {
        "ar": (
            "مرحباً بك في كيفا! 👋\n\n"
            "أنا وكيل المبيعات الذكي. يسعدني مساعدتك في اختيار المسار التدريبي المناسب لك.\n\n"
            "ما الذي تبحث عنه؟ هل تريد تطوير مهاراتك في الأمن السيبراني، تحليل البيانات، البرمجة، أم مجال آخر؟"
        ),
        "en": (
            "Welcome to Kayfa! 👋\n\n"
            "I'm your AI sales agent. I'm here to help you choose the right training path.\n\n"
            "What are you looking for? Cybersecurity, Data Analytics, Programming, or something else?"
        ),
    },
    "ticket_saved": {
        "ar": "✅ تم تسجيلك كعميل محتمل! سيتواصل معك أحد مندوبي المبيعات قريباً.",
        "en": "✅ You've been registered as a lead! A sales rep will contact you soon.",
    },
    # Page 2 — CRM
    "crm_filter_status": {"ar": "حالة العميل", "en": "Lead Status"},
    "crm_filter_course": {"ar": "الدورة / المسار", "en": "Course / Track"},
    "crm_refresh": {"ar": "🔄 تحديث", "en": "🔄 Refresh"},
    "crm_no_tickets": {
        "ar": "لا توجد تذاكر تطابق الفلاتر المحددة.",
        "en": "No tickets match the selected filters.",
    },
    "crm_total": {"ar": "إجمالي العملاء", "en": "Total Leads"},
    "crm_hot": {"ar": "ساخن 🔴", "en": "Hot 🔴"},
    "crm_warm": {"ar": "دافئ 🟡", "en": "Warm 🟡"},
    "crm_cold": {"ar": "بارد 🔵", "en": "Cold 🔵"},
}


def t(key: str, lang: str) -> str:
    """Translate a key."""
    return I18N.get(key, {}).get(lang, I18N.get(key, {}).get("ar", key))