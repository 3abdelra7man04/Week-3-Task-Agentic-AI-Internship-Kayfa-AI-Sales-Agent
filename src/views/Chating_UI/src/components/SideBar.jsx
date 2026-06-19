import React, { useState, useRef, useEffect } from "react";
import { useAppContext } from "../context/AppContext";
import { assets } from "../assets/assets/assets";
import { translations } from "../utils/languages";
import moment from "moment";
import { useNavigate } from "react-router-dom";

const SideBar = ({ isMenuOpen, setIsMenuOpen, setShowAuthOverlay }) => {
  const navigate = useNavigate();
  const {
    chats,
    selectChat,
    setSelectChat,
    theme,
    setTheme,
    user,
    token,
    logout,
    createNewChat,
    getChatMessages,
    language,
    deleteChat,
    renameChat
  } = useAppContext();

  const content = translations[language || 'en'];
  const [search, setSearch] = useState("");
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [activeMenuId, setActiveMenuId] = useState(null);

  // حالات جديدة للتعديل والتثبيت
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState("");
  const [pinnedChats, setPinnedChats] = useState(JSON.parse(localStorage.getItem("pinned_chats") || "[]"));

  const menuRef = useRef(null);
  const chatOptionsRef = useRef(null);

  // حفظ المحادثات المثبتة في التخزين المحلي
  useEffect(() => {
    localStorage.setItem("pinned_chats", JSON.stringify(pinnedChats));
  }, [pinnedChats]);

  const togglePin = (id) => {
    setPinnedChats(prev =>
      prev.includes(id) ? prev.filter(chatId => chatId !== id) : [...prev, id]
    );
    setActiveMenuId(null);
  };

  const handleRename = (id) => {
    if (editValue.trim()) {
      renameChat(id, editValue);
    }
    setEditingId(null);
  };

  // ترتيب المحادثات: المثبت أولاً ثم الأحدث
  const sortedChats = chats ? [...chats].sort((a, b) => {
    const aPinned = pinnedChats.includes(a._id);
    const bPinned = pinnedChats.includes(b._id);
    if (aPinned && !bPinned) return -1;
    if (!aPinned && bPinned) return 1;
    return new Date(b.updatedAt) - new Date(a.updatedAt);
  }) : [];

  const getInitials = (name) => {
    if (!name) return "GU";
    const names = name.split(" ");
    if (names.length >= 2) {
      return (names[0][0] + names[1][0]).toUpperCase();
    }
    return names[0][0].toUpperCase();
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowProfileMenu(false);
      }
      if (chatOptionsRef.current && !chatOptionsRef.current.contains(event.target)) {
        setActiveMenuId(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div
      className={`flex flex-col h-screen transition-all duration-500 ease-in-out z-20 
      ${theme === 'dark'
          ? 'bg-[#121212] border-white/10 text-white'
          : 'bg-white border-gray-200 text-gray-800'} 
      border-r relative
      ${isMenuOpen ? "w-72 p-5 opacity-100" : "w-0 p-0 opacity-0 pointer-events-none border-none"}
      max-md:absolute ${language === 'ar' ? 'right-0' : 'left-0'} 
      ${!isMenuOpen && (language === 'ar' ? 'translate-x-full' : '-translate-x-full')}
    `}
    >
      <div className={`${!isMenuOpen ? "hidden" : "block"} min-w-[240px] flex flex-col h-full`}>

        {/* Logo Section */}
        <div className="flex items-center gap-3">
          <img src={assets.logoooooo} alt="Logo" className="w-16 h-16 md:w-13 md:h-13 object-contain" />
          <div className="flex flex-col leading-tight">
            <p className="text-2xl font-black tracking-tighter">
              <span className={theme === 'dark' ? 'text-white' : 'text-gray-800'}>
                {language === 'ar' ? content.university : content.minia}
              </span>
            </p>
            <p className="text-sm font-black tracking-wide uppercase -mt-1">
              <span className="bg-gradient-to-r from-[#1A9BB3] to-[#3D81F6] bg-clip-text text-transparent">
                {language === 'ar' ? content.minia : content.university}
              </span>
            </p>
            <p className="text-[10px] font-bold tracking-wide uppercase text-gray-500 mt-0.5">
              {content.college}
            </p>
          </div>
        </div>

        {/* New Chat Button */}
        <button
          onClick={() => (token || user) ? createNewChat(navigate) : setShowAuthOverlay(true)}
          className={`flex justify-center items-center w-full py-2.5 mt-8 font-extrabold rounded-xl cursor-pointer transition-all duration-300 shadow-lg active:scale-95
          ${theme === 'dark' ? 'bg-[#1A9BB3] hover:bg-[#158296] text-white' : 'bg-[#1A9BB3] hover:bg-[#147e92] text-white'}`}
        >
          <span className="mx-2 text-xl font-light">+</span>
          <span className="text-sm tracking-wide">{content.newChat}</span>
        </button>

        {/* Search */}
        <div className={`flex items-center gap-2 px-3 py-2.5 mt-6 border transition-all duration-300 rounded-xl
          ${theme === 'dark' ? 'bg-white/5 border-white/10' : 'bg-[#F3F4F6] border-gray-200'}`}>
          <img src={assets.search_icon} className={`w-4 ${theme === 'dark' ? 'opacity-40' : 'opacity-60 invert'}`} alt="search" />
          <input
            onChange={(e) => setSearch(e.target.value)}
            value={search}
            type="text"
            placeholder={content.search}
            className="text-sm outline-none bg-transparent w-full font-bold"
          />
        </div>

        {/* Chats List */}
        <div className="flex-1 overflow-y-auto mt-8 space-y-1 custom-scrollbar">
          {(token || user) && sortedChats
            .filter(c => (c.name || "").toLowerCase().includes(search.toLowerCase()))
            .map((chat) => (
              <div
                key={chat._id}
                className={`group relative p-3 px-4 rounded-xl cursor-pointer flex justify-between items-center transition-all
                  ${selectChat?._id === chat._id
                    ? (theme === 'dark' ? 'bg-white/10' : 'bg-gray-100')
                    : (theme === 'dark' ? 'hover:bg-white/5' : 'hover:bg-gray-50')}`}
                onClick={() => {
                  if (editingId === chat._id) return;
                  setSelectChat(chat);
                  getChatMessages(chat._id);
                  navigate(`/app/c/${chat._id}`);
                  if (window.innerWidth < 768) setIsMenuOpen(false);
                }}
              >
                <div className="flex-1 min-w-0 flex items-center gap-2">
                  {/* أيقونة الدبوس إذا كان مثبت */}
                  {pinnedChats.includes(chat._id) && (
                    <svg className={`w-3 h-3 flex-shrink-0 ${theme === 'dark' ? 'text-[#1A9BB3]' : 'text-[#1A9BB3]'}`} fill="currentColor" viewBox="0 0 16 16">
                      <path d="M4.146.146A.5.5 0 0 1 4.5 0h7a.5.5 0 0 1 .5.5c0 .68-.342 1.174-.646 1.479-.126.125-.25.224-.354.298v4.431l.078.048c.203.127.476.314.751.555C12.36 7.775 13 8.527 13 9.5a.5.5 0 0 1-.5.5h-4v4.5c0 .276-.224.5-.5.5s-.5-.224-.5-.5V10h-4a.5.5 0 0 1-.5-.5c0-.973.64-1.725 1.17-2.189A5.921 5.921 0 0 1 5 6.755V2.327a1.777 1.777 0 0 1-.354-.298C4.342 1.726 4 1.232 4 .5a.5.5 0 0 1 .146-.354z" />
                    </svg>
                  )}

                  <div className="flex-1 min-w-0">
                    {editingId === chat._id ? (
                      <input
                        autoFocus
                        className="w-full bg-transparent border-b border-[#1A9BB3] outline-none text-sm font-bold"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={() => handleRename(chat._id)}
                        onKeyDown={(e) => e.key === 'Enter' && handleRename(chat._id)}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <p className={`truncate text-sm font-bold ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                        {chat.name || "New Chat"}
                      </p>
                    )}
                    <p className="text-[10px] font-medium text-gray-400 mt-1">{moment(chat.updatedAt).format('ll')}</p>
                  </div>
                </div>

                <div className="relative ml-2" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => setActiveMenuId(activeMenuId === chat._id ? null : chat._id)}
                    className={`opacity-0 group-hover:opacity-100 p-1 rounded-lg transition-all
                      ${theme === 'dark' ? 'hover:bg-white/10 text-gray-400' : 'hover:bg-gray-200 text-gray-600'}`}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M3 9.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z" />
                    </svg>
                  </button>

                  {activeMenuId === chat._id && (
                    <div
                      ref={chatOptionsRef}
                      className={`absolute top-full ${language === 'ar' ? 'left-0' : 'right-0'} z-30 mt-1 w-32 rounded-xl shadow-2xl border overflow-hidden animate-in fade-in zoom-in-95
                        ${theme === 'dark' ? 'bg-[#1e1e1e] border-white/10' : 'bg-white border-gray-100'}`}
                    >
                      {/* زر التثبيت */}
                      <button
                        onClick={() => togglePin(chat._id)}
                        className={`flex items-center justify-between w-full p-2.5 text-[11px] font-bold transition-all
                          ${theme === 'dark' ? 'hover:bg-white/5 text-gray-300' : 'hover:bg-gray-50 text-gray-700'}`}
                      >
                        <span>{pinnedChats.includes(chat._id) ? (language === 'ar' ? 'إلغاء التثبيت' : 'Unpin') : (language === 'ar' ? 'تثبيت' : 'Pin')}</span>
                        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 16 16"><path d="M4.146.146A.5.5 0 0 1 4.5 0h7a.5.5 0 0 1 .5.5c0 .68-.342 1.174-.646 1.479-.126.125-.25.224-.354.298v4.431l.078.048c.203.127.476.314.751.555C12.36 7.775 13 8.527 13 9.5a.5.5 0 0 1-.5.5h-4v4.5c0 .276-.224.5-.5.5s-.5-.224-.5-.5V10h-4a.5.5 0 0 1-.5-.5c0-.973.64-1.725 1.17-2.189A5.921 5.921 0 0 1 5 6.755V2.327a1.777 1.777 0 0 1-.354-.298C4.342 1.726 4 1.232 4 .5a.5.5 0 0 1 .146-.354z" /></svg>
                      </button>

                      {/* زر التعديل */}
                      <button
                        onClick={() => {
                          setEditingId(chat._id);
                          setEditValue(chat.name);
                          setActiveMenuId(null);
                        }}
                        className={`flex items-center justify-between w-full p-2.5 text-[11px] font-bold transition-all
                          ${theme === 'dark' ? 'hover:bg-white/5 text-gray-300' : 'hover:bg-gray-50 text-gray-700'}`}
                      >
                        <span>{language === 'ar' ? 'تعديل' : 'Rename'}</span>
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                      </button>

                      <button
                        onClick={() => {
                          deleteChat(chat._id);
                          setActiveMenuId(null);
                        }}
                        className={`flex items-center justify-between w-full p-2.5 text-[11px] font-bold transition-all
                          ${theme === 'dark' ? 'hover:bg-red-500/10 text-red-400' : 'hover:bg-red-50 text-red-500'}`}
                      >
                        <span>{language === 'ar' ? 'حذف' : 'Delete'}</span>
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
        </div>

        {/* Footer Profile Section */}
        <div className="mt-auto pt-4 border-t relative" ref={menuRef}>
          {showProfileMenu && (token || user) && (
            <div className={`absolute bottom-full left-0 w-full mb-2 p-2 rounded-2xl shadow-2xl border transition-all animate-in fade-in slide-in-from-bottom-2
              ${theme === 'dark' ? 'bg-[#1e1e1e] border-white/10' : 'bg-white border-gray-200'}`}>

              <div className="flex items-center justify-between p-3">
                <span className="text-sm font-black">{content.darkMode}</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={theme === 'dark'}
                    onChange={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#1A9BB3]"></div>
                </label>
              </div>

              <div onClick={() => { logout(); setShowProfileMenu(false); }}
                className={`flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all border border-transparent
                    ${theme === 'dark' ? 'hover:bg-red-500/10 text-red-400' : 'hover:bg-red-50 text-red-500'}`}>
                <span className="text-sm font-black tracking-wide">{content.logout}</span>
                <img src={assets.logout_icon} className={`w-4 h-4 ${theme === 'dark' ? '' : 'invert'} opacity-80`} alt="logout" />
              </div>
            </div>
          )}

          <div
            onClick={() => (token || user) ? setShowProfileMenu(!showProfileMenu) : setShowAuthOverlay(true)}
            className={`flex items-center gap-3 p-3 rounded-xl transition-all cursor-pointer border
            ${theme === 'dark'
                ? 'hover:bg-white/5 border-transparent active:bg-white/10'
                : 'hover:bg-gray-50 border-transparent active:bg-gray-100'}
            ${showProfileMenu && (theme === 'dark' ? 'bg-white/5 border-white/10' : 'bg-gray-50 border-gray-200')}`}
          >
            <div className="w-9 h-9 min-w-[36px] rounded-full flex items-center justify-center bg-gradient-to-br from-[#1A9BB3] to-[#3D81F6] text-white text-xs font-black shadow-sm border border-white/20">
              {getInitials(user?.name)}
            </div>
            <div className="flex-1 min-w-0">
              <p className={`text-xs font-black truncate ${theme === 'dark' ? 'text-white' : 'text-gray-700'}`}>
                {(token || user) ? (user?.name || "Loading...") : content.loginAccount}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SideBar;