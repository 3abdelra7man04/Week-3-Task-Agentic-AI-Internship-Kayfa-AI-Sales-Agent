import { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

export const AppContext = createContext();

export const AppContextProvider = (props) => {
    // 1. الحالة الأساسية
    const [token, setToken] = useState(localStorage.getItem('token') || "");
    const [user, setUser] = useState(null);
    const [chats, setChats] = useState([]);
    const [selectChat, setSelectChat] = useState(null);
    const [messages, setMessages] = useState([]);
    const [theme, setTheme] = useState(localStorage.getItem('theme') || "light");
    const [language, setLanguage] = useState(localStorage.getItem('language') || "en");

    const backendUrl = "http://127.0.0.1:5000";

    // 2. إدارة الاتجاه واللغة
    useEffect(() => {
        document.body.dir = language === 'ar' ? 'rtl' : 'ltr';
        localStorage.setItem('language', language);
    }, [language]);

    useEffect(() => {
        localStorage.setItem('theme', theme);
    }, [theme]);

    // 3. تحميل بيانات المستخدم
    const loadUserData = async () => {
        if (!token) return;
        try {
            const projectId = 0;
            const { data } = await axios.get(`${backendUrl}/api/v1/user/get-profile/${projectId}?user_id=${token}`, { headers: { token } });
            if (data.userData) {
                setUser({
                    id: data.userData.id,
                    name: data.userData.user_name,
                    email: data.userData.user_email,
                });
            }
        } catch (e) { console.error("Error loading user data:", e); }
    };

    // 4. تحميل قائمة المحادثات
    const loadUserChats = async () => {
        if (!token) return;
        try {
            const projectId = "0";
            const { data } = await axios.get(`${backendUrl}/api/v1/chat/${projectId}/list/${token}`, { headers: { token } });

            if (data && data.all_chats) {
                const mappedChats = data.all_chats.map((c) => ({
                    _id: c._id,
                    name: c.chat_title || "Untitled Chat",
                    messages: [],
                    updatedAt: c.updatedAt || new Date()
                }));
                setChats(mappedChats);
            }
        } catch (e) { console.error("Error loading chats:", e); }
    };

    // 5. جلب الرسائل
    const getChatMessages = async (chatId) => {
        try {
            const projectId = "0";
            const { data } = await axios.get(`${backendUrl}/api/v1/chat/${projectId}/get/${chatId}`, { headers: { token } });
            if (data && data.chat_conversation) {
                const mapped = data.chat_conversation.flatMap(({ question, answer }) => [
                    { role: "user", content: question },
                    { role: "assistant", content: answer },
                ]);
                setMessages(mapped);
            } else if (data && data.chat_history) {
                setMessages(data.chat_history);
            }
        } catch (e) {
            console.error(e);
            setMessages([]);
        }
    };

    // --- التعديلات الجديدة (الحذف والتعديل) ---

    // 6. حذف المحادثة
    const deleteChat = async (chatId) => {
        try {
            const projectId = "0";
            // طلب الحذف من الباك اند
            await axios.delete(`${backendUrl}/api/v1/chat/${projectId}/delete/${chatId}`, { headers: { token } });

            // تحديث القائمة محلياً فوراً
            setChats(prev => prev.filter(c => c._id !== chatId));

            // إذا كانت المحادثة المحذوفة هي النشطة حالياً، قم بتفريغ الشاشة
            if (selectChat?._id === chatId) {
                setSelectChat(null);
                setMessages([]);
            }
        } catch (e) {
            console.error("Error deleting chat:", e);
        }
    };

    // 7. تعديل اسم المحادثة
    const renameChat = async (chatId, newName) => {
        if (!newName.trim()) return;
        try {
            const projectId = "0";
            // طلب التعديل من الباك اند
            await axios.put(`${backendUrl}/api/v1/chat/${projectId}/rename/${chatId}`,
                { new_title: newName },
                { headers: { token } }
            );

            // تحديث الاسم في القائمة المحلية فوراً
            setChats(prev => prev.map(c => c._id === chatId ? { ...c, name: newName } : c));
        } catch (e) {
            console.error("Error renaming chat:", e);
        }
    };

    // --- نهاية التعديلات الجديدة ---

    // 8. إرسال سؤال
    const sendPrompt = async (prompt) => {
        if (!prompt.trim()) return null;
        try {
            const userMsg = { role: "user", content: prompt };
            setMessages(prev => [...(prev || []), userMsg]);

            const projectId = "0";
            let response;
            let isNewChat = false;

            if (!selectChat?._id) {
                isNewChat = true;
                response = await axios.post(`${backendUrl}/api/v1/chat/${projectId}`, {
                    query: prompt,
                    user_id: token ? token : null,
                    is_guest: !token,
                    limit: 3
                }, { headers: { token } });
            } else {
                response = await axios.post(`${backendUrl}/api/v1/chat/${projectId}/c/${selectChat._id}`, {
                    query: prompt,
                    user_id: token ? token : null,
                    is_guest: !token,
                    limit: 3
                }, { headers: { token } });
            }

            const data = response.data;
            if (data && data.answer) {
                const botMessage = { role: "assistant", content: data.answer };
                setMessages(prev => [...(prev || []), botMessage]);
                loadUserChats();
                if (isNewChat && data.chat_id) {
                    setSelectChat({ _id: data.chat_id });
                    return data.chat_id;
                }
            }
        } catch (e) {
            console.error("Backend error:", e);
            const errorMessage = {
                role: "assistant",
                content: "Sorry, I couldn't reach the AI backend. Please check your connection!"
            };
            setMessages(prev => [...(prev || []), errorMessage]);
        }
        return null;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(""); setUser(null); setChats([]); setMessages([]); setSelectChat(null);
    };

    useEffect(() => {
        if (token) { loadUserData(); loadUserChats(); }
    }, [token]);

    const value = {
        token, setToken,
        user, setUser,
        chats, setChats,
        selectChat, setSelectChat,
        messages, setMessages,
        theme, setTheme,
        language, setLanguage,
        backendUrl,
        logout,
        sendPrompt,
        getChatMessages,
        deleteChat, // إضافة الدالة هنا
        renameChat, // إضافة الدالة هنا
        createNewChat: (navigate) => {
            setSelectChat(null);
            setMessages([]);
            if (navigate) navigate('/app');
        }
    };

    return <AppContext.Provider value={value}>{props.children}</AppContext.Provider>;
};

export const useAppContext = () => useContext(AppContext);