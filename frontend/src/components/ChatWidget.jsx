import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, X, Bot, User, Minimize2, Maximize2, Sparkles, Trash2, Zap, MapPin, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [isVisible, setIsVisible] = useState(false);
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([
        { role: 'assistant', text: "Hello! I am **Infinite AI**, your dedicated event assistant. How can I help you explore Chennai today?" }
    ]);
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef(null);

    // Global listener to open chat from anywhere
    useEffect(() => {
        const handleOpenChat = async (e) => {
            setIsVisible(true);
            setIsOpen(true);
            setIsMinimized(false);
            if (e.detail?.prompt) {
                const triggerMsg = e.detail.prompt;
                setChatHistory([{ role: 'user', text: triggerMsg }]);
                setIsTyping(true);

                try {
                    const token = localStorage.getItem('token');
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            ...(token && { 'Authorization': `Bearer ${token}` })
                        },
                        body: JSON.stringify({
                            message: triggerMsg,
                            user_location: "Chennai",
                            current_page: window.location.pathname
                        }),
                    });

                    if (res.ok) {
                        const data = await res.json();
                        setChatHistory(prev => [...prev, { role: 'assistant', text: data.reply }]);
                    } else {
                        throw new Error(`Server returned ${res.status}`);
                    }
                } catch (err) {
                    console.error("Auto Chat Error:", err);
                    setChatHistory(prev => [...prev, { role: 'assistant', text: "_Error:_ Unable to reach Infinite AI Core. Please check backend connection." }]);
                } finally {
                    setIsTyping(false);
                }
            }
        };

        window.addEventListener('open-chat', handleOpenChat);
        return () => window.removeEventListener('open-chat', handleOpenChat);
    }, []);



    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [chatHistory, isTyping, isOpen, isMinimized]);

    const handleSendMessage = async (inputMessage) => {
        const userMessage = typeof inputMessage === 'string' ? inputMessage : message.trim();
        if (!userMessage) return;

        if (typeof inputMessage !== 'string') setMessage('');

        setChatHistory(prev => [...prev, { role: 'user', text: userMessage }]);
        setIsTyping(true);

        try {
            const location = "Chennai";
            const page = window.location.pathname;

            const token = localStorage.getItem('token');
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token && { 'Authorization': `Bearer ${token}` })
                },
                body: JSON.stringify({
                    message: userMessage,
                    user_location: location,
                    current_page: page
                }),
            });

            if (res.ok) {
                const data = await res.json();
                setChatHistory(prev => [...prev, { role: 'assistant', text: data.reply }]);
            } else {
                throw new Error("Link severed");
            }
        } catch (err) {
            console.error("Chat Error:", err);
            setChatHistory(prev => [...prev, { role: 'assistant', text: "_Error:_ I've lost connection to my neural core. Please try again in a moment." }]);
        } finally {
            setIsTyping(false);
        }
    };

    const clearChat = () => {
        if (window.confirm("Purge conversation history?")) {
            setChatHistory([{ role: 'assistant', text: "Memory purged. How can I assist you now?" }]);
        }
    };

    // Fail-safe for ReactMarkdown - Fixed by removing className from component and using wrapper div
    const SafeMarkdown = ({ text }) => {
        try {
            return (
                <div className="prose prose-invert prose-sm prose-p:leading-relaxed prose-pre:bg-slate-900/50 max-w-full overflow-x-hidden">
                    <ReactMarkdown>{text || ""}</ReactMarkdown>
                </div>
            );
        } catch (err) {
            console.error("Markdown rendering failed", err);
            return <div className="text-slate-200 whitespace-pre-wrap">{text}</div>;
        }
    };

    if (!isVisible) return null;

    return (
        <div className="fixed bottom-8 right-8 z-[9999] flex flex-col items-end pointer-events-none">
            {/* Launcher Button */}
            <div className="pointer-events-auto">
                <motion.button
                    type="button"
                    onClick={() => {
                        console.log("Toggle ChatWidget:", !isOpen);
                        setIsOpen(!isOpen);
                    }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-500 rounded-full flex items-center justify-center text-white shadow-[0_8px_32px_rgba(8,145,178,0.4)] border border-white/20 active:shadow-inner overflow-hidden relative cursor-pointer"
                >
                    <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(255,255,255,0.2),transparent)] pointer-events-none"></div>
                    <AnimatePresence mode="wait">
                        {isOpen ? (
                            <motion.div
                                key="close"
                                initial={{ opacity: 0, rotate: -90, scale: 0.5 }}
                                animate={{ opacity: 1, rotate: 0, scale: 1 }}
                                exit={{ opacity: 0, rotate: 90, scale: 0.5 }}
                                transition={{ duration: 0.2 }}
                            >
                                <X size={28} />
                            </motion.div>
                        ) : (
                            <motion.div
                                key="open"
                                initial={{ opacity: 0, rotate: 90, scale: 0.5 }}
                                animate={{ opacity: 1, rotate: 0, scale: 1 }}
                                exit={{ opacity: 0, rotate: -90, scale: 0.5 }}
                                transition={{ duration: 0.2 }}
                            >
                                <MessageSquare size={28} />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.button>
            </div>

            {/* Chat Widget Panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 100, originX: 1, originY: 1 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 100 }}
                        transition={{ type: "spring", damping: 25, stiffness: 300 }}
                        className={`fixed z-[9990] flex flex-col overflow-hidden rounded-[2rem] border border-white/20 bg-slate-900/80 shadow-[0_32px_128px_rgba(0,0,0,0.6)] backdrop-blur-[20px] pointer-events-auto transition-all duration-300 ${isMinimized ? 'w-[360px] h-20 bottom-24 right-8' : 'w-[95vw] md:w-[80vw] max-w-5xl h-[85vh] m-auto inset-0'}`}
                    >
                        <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 p-4 flex items-center justify-between border-b border-white/10 relative overflow-hidden">
                            <div className="absolute inset-0 bg-white/5 opacity-30 blur-2xl pointer-events-none"></div>
                            <div className="flex items-center gap-3 relative z-10">
                                <div className="w-9 h-9 bg-white/10 rounded-xl flex items-center justify-center border border-white/20 shadow-lg">
                                    <Sparkles className="text-primary-400" size={18} />
                                </div>
                                <h3 className="font-extrabold text-white text-md tracking-tight">Infinite AI</h3>
                            </div>
                            <div className="flex items-center gap-0.5 relative z-10">
                                <button type="button" onClick={clearChat} className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-red-400 transition-all active:scale-95" title="Purge Cache">
                                    <Trash2 size={16} />
                                </button>
                                <button type="button" onClick={() => setIsMinimized(!isMinimized)} className="p-2 hover:bg-white/10 rounded-xl text-slate-400 hover:text-white transition-all active:scale-95">
                                    {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
                                </button>
                            </div>
                        </div>

                        {!isMinimized && (
                            <>
                                {/* Conversation Area */}
                                <div
                                    ref={scrollRef}
                                    className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 md:space-y-8 no-scroll scroll-smooth bg-gradient-to-b from-transparent to-slate-950/20 shadow-inner"
                                >
                                    {chatHistory.map((chat, index) => (
                                        <div key={index} className={`flex ${chat.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`flex gap-4 max-w-[88%] ${chat.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                                <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 border shadow-lg ${chat.role === 'user'
                                                    ? 'bg-gradient-to-br from-primary-500 to-primary-600 border-primary-400 text-white'
                                                    : 'bg-white/10 border-white/10 text-slate-300'
                                                    }`}>
                                                    {chat.role === 'user' ? <User size={16} /> : <Zap size={16} className="text-primary-400" />}
                                                </div>
                                                <div className={`p-4 rounded-[1.5rem] text-[15px] leading-relaxed shadow-xl ${chat.role === 'user'
                                                    ? 'bg-primary-600/30 border border-primary-400/30 text-white rounded-tr-none'
                                                    : 'bg-white/10 border border-white/10 text-slate-200 rounded-tl-none backdrop-blur-md'
                                                    }`}>
                                                    <SafeMarkdown text={chat.text} />
                                                </div>
                                            </div>
                                        </div>
                                    ))}

                                    {isTyping && (
                                        <div className="flex justify-start">
                                            <div className="flex gap-4">
                                                <div className="w-9 h-9 rounded-xl bg-white/10 border border-white/10 flex items-center justify-center">
                                                    <Activity size={16} className="text-primary-400 animate-pulse" />
                                                </div>
                                                <div className="bg-white/10 border border-white/10 p-5 rounded-[1.5rem] rounded-tl-none flex gap-1.5 items-center">
                                                    <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1 }} className="w-2 h-2 bg-primary-500 rounded-full"></motion.div>
                                                    <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-2 h-2 bg-primary-500 rounded-full"></motion.div>
                                                    <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-2 h-2 bg-primary-500 rounded-full"></motion.div>
                                                </div>
                                            </div>
                                        </div>
                                    )}


                                </div>

                                <div className="p-6 bg-gradient-to-t from-slate-950/80 to-transparent border-t border-white/5">
                                    <form
                                        onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
                                        className="relative group flex items-center gap-3"
                                    >
                                        <div className="relative flex-1 group/input">
                                            <div className="absolute inset-0 bg-primary-500/10 rounded-2xl opacity-0 group-focus-within/input:opacity-100 transition-opacity blur-xl"></div>
                                            <input
                                                type="text"
                                                value={message}
                                                onChange={(e) => setMessage(e.target.value)}
                                                placeholder="Initialize query..."
                                                className="w-full bg-white/5 border border-white/10 rounded-2xl pl-5 pr-14 py-4 text-sm text-white focus:outline-none focus:border-primary-500/50 focus:bg-white/10 transition-all placeholder:text-slate-500 relative z-10 backdrop-blur-md"
                                            />
                                            <button
                                                type="submit"
                                                disabled={!message.trim() || isTyping}
                                                className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 hover:from-primary-400 hover:to-primary-500 text-white rounded-xl flex items-center justify-center transition-all disabled:opacity-20 disabled:grayscale shadow-lg shadow-primary-500/20 active:scale-95 z-20"
                                            >
                                                <Send size={18} strokeWidth={2.5} />
                                            </button>
                                        </div>
                                    </form>
                                    <div className="flex items-center justify-center gap-3 mt-5 opacity-30">
                                        <div className="h-[1px] flex-1 bg-gradient-to-r from-transparent to-slate-700"></div>
                                        <span className="text-[8px] font-black uppercase tracking-[0.3em] text-slate-500">
                                            Infinite Engine v2.0
                                        </span>
                                        <div className="h-[1px] flex-1 bg-gradient-to-l from-transparent to-slate-700"></div>
                                    </div>
                                </div>
                            </>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
