"""
_style.py — Shared Kayfa brand styles for Streamlit pages.
Inject via inject_styles(lang) at the top of each page.
"""

import streamlit as st


def lang_toggle(default: str = "ar") -> str:
    """Render a language toggle and return 'ar' or 'en'."""
    if "lang" not in st.session_state:
        st.session_state["lang"] = default

    col1, col2 = st.columns([8, 2])
    with col2:
        options = ["🇸🇦 العربية", "🇬🇧 English"]
        idx = 0 if st.session_state["lang"] == "ar" else 1
        chosen = st.selectbox(
            label="",
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
