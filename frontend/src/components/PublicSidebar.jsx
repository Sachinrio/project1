import React, { useState } from 'react';
import { Compass, Mountain, Share2, LogIn, UserPlus, Menu, X } from 'lucide-react';

export const PublicSidebar = ({ onLogin, onSignup, onDiscover, onSummit, onNetwork }) => {
    const [isOpen, setIsOpen] = useState(false);
    const menuItems = [
        { label: 'Discover', icon: Compass, action: onDiscover },
        { label: 'Summits', icon: Mountain, action: onSummit },
        { label: 'Network', icon: Share2, action: onNetwork },
    ];

    const toggleSidebar = () => setIsOpen(!isOpen);

    return (
        <>
            {/* Mobile Menu Button - Fixed outside the sidebar */}
            <button
                onClick={toggleSidebar}
                className="lg:hidden fixed top-6 left-6 z-[60] p-3 bg-white border border-slate-200 text-slate-900 rounded-2xl shadow-xl hover:bg-slate-50 transition-all active:scale-95"
            >
                {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Backdrop for mobile */}
            {isOpen && (
                <div
                    className="lg:hidden fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 transition-opacity duration-300"
                    onClick={() => setIsOpen(false)}
                />
            )}

            <aside className={`fixed top-0 left-0 h-screen w-64 bg-[#EEF2FF] flex flex-col z-50 transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
                {/* Logo Area */}
                <div className="h-24 flex items-center px-8">
                    <div className="flex items-center gap-3 cursor-pointer group">
                        <div className="w-10 h-10 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:rotate-12 transition-transform">
                            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <span className="text-xl font-black tracking-tight text-slate-900 group-hover:text-indigo-600 transition-colors">
                            IBZ
                        </span>
                    </div>
                </div>

                {/* Navigation Links */}
                <nav className="flex-1 py-8 px-6 space-y-2 overflow-y-auto">
                    {menuItems.map((item, idx) => (
                        <a
                            key={idx}
                            href="#"
                            onClick={(e) => {
                                e.preventDefault();
                                if (item.action) item.action();
                                setIsOpen(false); // Close on click for mobile
                            }}
                            className="flex items-center gap-4 px-4 py-3.5 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-50 transition-all group relative overflow-hidden"
                        >
                            <item.icon size={22} className="group-hover:text-indigo-600 transition-colors shrink-0" />
                            <span className="font-bold tracking-wide text-sm">{item.label}</span>

                            {/* Hover Glow */}
                            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/0 via-indigo-500/5 to-indigo-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                        </a>
                    ))}
                </nav>
            </aside>
        </>
    );
};
