
import React from "react";
import { assets } from "../assets/assets/assets";
import moment from "moment";
import Markdown from "react-markdown";
import { useAppContext } from "../context/AppContext";

const Message = ({ message }) => {
  const { theme } = useAppContext();
  
  // التأكد من أن الدور هو 'user' أو 'assistant' كما هو معتاد في FastAPI
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} items-start gap-3 my-4 animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      
      {/* أيقونة البوت (Uni) */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#1A9BB3] to-[#3D81F6] flex items-center justify-center text-white text-[10px] font-bold shadow-sm flex-shrink-0">
          Uni
        </div>
      )}

      <div className={`flex flex-col gap-1 max-w-[85%] md:max-w-2xl`}>
        <div className={`p-3 px-4 rounded-2xl border transition-all duration-300 text-sm md:text-base shadow-sm
          ${isUser 
            ? "bg-white dark:bg-[#252525] border-gray-200 dark:border-white/5 text-gray-800 dark:text-gray-100 rounded-tr-none" 
            : "bg-[#1A9BB3] border-[#1A9BB3] text-white rounded-tl-none" 
          }`}
        >
          {/* استخدام prose لضمان تنسيق الـ Markdown (أكواد، قوائم، إلخ) بشكل صحيح */}
          <div className={`prose prose-sm max-w-none ${!isUser ? "prose-invert" : theme === 'dark' ? "prose-invert" : ""}`}>
            <Markdown>{message.content || ""}</Markdown>
          </div>
        </div>

        {/* التوقيت مع معالجة حالة عدم وجود timestamp من الباك اند فوراً */}
        <span className={`text-[10px] px-1 opacity-50 ${isUser ? "text-right" : "text-left"}`}>
          {message.createdAt || message.timestamp 
            ? moment(message.createdAt || message.timestamp).fromNow() 
            : moment().fromNow()}
        </span>
      </div>

      {/* أيقونة المستخدم */}
      {isUser && (
        <img 
          src={assets.user_icon} 
          className="w-8 h-8 rounded-full border border-gray-200 dark:border-white/10 flex-shrink-0 object-cover" 
          alt="User" 
        />
      )}
    </div>
  );
};

export default Message;