import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      "new_chat": "New Chat",
      "search": "Search chats...",
      "welcome_hi": "Hi",
      "welcome_ask": "How can I help you today?",
      "input_placeholder": "Ask UniAsk anything...",
      "thinking": "UniAsk is thinking...",
      "power_by": "Powered by",
      "guest": "Guest",
      "login": "Login",
      "logout": "Logout",
      "dark_mode": "Dark Mode"
    }
  },
  ar: {
    translation: {
      "new_chat": "محادثة جديدة",
      "search": "البحث في المحادثات...",
      "welcome_hi": "أهلاً",
      "welcome_ask": "كيف يمكنني مساعدتك اليوم؟",
      "input_placeholder": "اسأل UniAsk أي شيء...",
      "thinking": "جاري التفكير...",
      "power_by": "مشغل بواسطة",
      "guest": "زائر",
      "login": "تسجيل الدخول",
      "logout": "تسجيل الخروج",
      "dark_mode": "الوضع الليلي"
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    interpolation: { escapeValue: false }
  });

// تغيير اتجاه الصفحة فور تغيير اللغة
i18n.on('languageChanged', (lng) => {
  document.body.dir = lng === 'ar' ? 'rtl' : 'ltr';
});

export default i18n;