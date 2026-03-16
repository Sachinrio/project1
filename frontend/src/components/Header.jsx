
import React, { useState, useEffect } from 'react';

export const Header = ({ onExport, onLogin, onSignup }) => {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <header className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-500 ${scrolled ? 'bg-white/90 backdrop-blur-xl h-16 shadow-sm border-b border-slate-100' : 'bg-transparent h-24'
            }`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center justify-between">
                <div className="flex items-center gap-12">
                    <div className="flex items-center gap-3 cursor-pointer group">
                        <div className="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center transition-transform group-hover:rotate-12">
                            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <span className="text-2xl font-black tracking-tighter text-slate-950 group-hover:text-indigo-600 transition-colors">IBZ</span>
                    </div>

                    <nav className="hidden lg:flex items-center gap-10">
                        <HeaderLink label="Discover" />
                        <HeaderLink label="Summits" />
                        <HeaderLink label="Network" />
                    </nav>
                </div>

                <div className="flex items-center gap-6">
                    <button onClick={onLogin} className="text-sm font-black uppercase tracking-widest text-slate-500 hover:text-slate-950 transition-colors">Log In</button>
                    <button onClick={onSignup} className="bg-slate-900 text-white text-[11px] font-black uppercase tracking-widest px-8 py-3.5 rounded-2xl hover:bg-indigo-600 transition-all btn-bounce shadow-xl shadow-indigo-100">
                        Join Hub
                    </button>
                </div>
            </div>
        </header>
    );
};

const HeaderLink = ({ label }) => (
    <a href="#" className="text-sm font-black uppercase tracking-widest text-slate-400 hover:text-slate-950 transition-all relative group">
        {label}
        <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-indigo-600 group-hover:w-full transition-all duration-300"></span>
    </a>
);
