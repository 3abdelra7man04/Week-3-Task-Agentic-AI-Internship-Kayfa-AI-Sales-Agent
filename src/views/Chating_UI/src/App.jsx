import './App.css'
import SideBar from "./components/SideBar"
import { Route, Routes, Navigate } from 'react-router-dom'
import ChatBox from "./components/ChatBox"
import { useState } from 'react'
import { assets } from './assets/assets/assets'
import { useAppContext } from './context/AppContext'
import Login from './pages/Login'
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  // استدعاء القيم الجديدة (language, setLanguage) من الـ Context
  const { user, theme, token, language, setLanguage } = useAppContext() 
  
  const [isMenuOpen, setIsMenuOpen] = useState(true)
  const [showAuthOverlay, setShowAuthOverlay] = useState(false)

  return (
    <div 
      dir={language === 'ar' ? 'rtl' : 'ltr'} // تحديد اتجاه التطبيق بالكامل بناءً على اللغة
      className={`min-h-screen w-full transition-colors duration-500 
      ${theme === 'dark' ? 'bg-[#121212] text-white' : 'bg-[#F3F4F6] text-[#1a1a1a]'}`}
    >
      
      <ToastContainer theme={theme === 'dark' ? 'dark' : 'light'} />

      {/* زرار تبديل اللغة - يتغير مكانه وتنسيقه بناءً على اللغة والثيم */}
      <button 
        onClick={() => setLanguage(language === 'en' ? 'ar' : 'en')}
        className={`fixed top-6 z-[100] px-4 py-2 rounded-full font-bold shadow-lg transition-all duration-500 active:scale-95
          ${language === 'en' ? 'right-6' : 'left-6'} 
          ${theme === 'dark' ? 'bg-white/10 text-white border border-white/20' : 'bg-white text-[#1A9BB3] border border-gray-200'}`}
      >
        {language === 'en' ? 'العربية' : 'English'}
      </button>

      {/* زرار المنيو (الشرط) - يتحرك ديناميكياً مع السايد بار حسب اتجاه اللغة */}
      <button 
        onClick={() => setIsMenuOpen(!isMenuOpen)}
        className={`fixed top-6 z-[60] p-2 transition-all duration-500 ease-in-out
          ${language === 'ar' 
            ? (isMenuOpen ? "right-[235px]" : "right-6") 
            : (isMenuOpen ? "left-[235px]" : "left-6")
          } 
          hover:scale-110 active:scale-90`}
      >
        <img 
          src={assets.menu_icon} 
          className={`w-7 h-7 ${theme === 'dark' ? 'invert-0' : 'invert'} opacity-60 hover:opacity-100`} 
          alt="menu" 
        />
      </button>

      <div className='flex h-screen overflow-hidden relative'>
        
        <SideBar 
          isMenuOpen={isMenuOpen} 
          setIsMenuOpen={setIsMenuOpen} 
          setShowAuthOverlay={setShowAuthOverlay} 
        />
        
        <div className="flex-1 h-full relative">
          
          <div className={`h-full transition-all duration-500 
            ${(showAuthOverlay && !token) ? 'blur-2xl pointer-events-none scale-95' : 'scale-100'}`}>
            <Routes>
              {/* دعم المسار الرئيسي والمسار الفرعي للمحادثات */}
              <Route path='/app' element={<ChatBox />} />
              <Route path='/app/c/:chatId' element={<ChatBox />} />
              
              {/* توجيه أي مسار آخر إلى /app لضمان استقرار التطبيق */}
              <Route path='*' element={<Navigate to="/app" />} />
            </Routes>
          </div>

          {/* نافذة التسجيل المنبثقة (Auth Overlay) */}
          {showAuthOverlay && !token && (
            <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-[2px] animate-in fade-in duration-300">
              <div className="relative animate-in slide-in-from-bottom-5 duration-500">
                
                {/* زر إغلاق النافذة - يتغير مكانه حسب اللغة */}
                <button 
                  onClick={() => setShowAuthOverlay(false)}
                  className={`absolute -top-12 bg-white/10 hover:bg-white/20 text-white w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-lg
                    ${language === 'ar' ? 'left-0' : 'right-0'}`}
                >
                  ✕
                </button>

                <Login setShowAuthOverlay={setShowAuthOverlay} />
                
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App