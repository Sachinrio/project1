import { X, FileText, Shield, Download, ChevronRight } from 'lucide-react';

export function TermsModal({ onClose }) {
    return (
        <div className="fixed inset-0 z-[100] bg-slate-950/90 backdrop-blur-sm flex items-center justify-end animate-in fade-in duration-200">
            {/* Click outside to close */}
            <div className="absolute inset-0" onClick={onClose} />

            {/* Slide-over Panel */}
            <div className="relative w-full max-w-2xl h-full bg-[#0B1221] border-l border-white/10 shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
                {/* Header */}
                <div className="flex items-center justify-between px-8 py-6 border-b border-white/5 bg-[#0B1221]">
                    <div>
                        <h2 className="text-xl font-bold text-white">Terms and Conditions</h2>
                        <p className="text-xs text-slate-500 mt-1">Last updated: October 24, 2023</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <button
                            onClick={onClose}
                            className="flex items-center gap-2 text-xs font-bold text-sky-500 hover:text-sky-400 transition-colors bg-sky-500/10 px-3 py-1.5 rounded-lg"
                        >
                            Back to Sign Up
                            <X size={14} />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                    <div className="prose prose-invert prose-sm max-w-none">
                        <h1 className="text-3xl font-bold text-white mb-8">User Agreement</h1>

                        <p className="text-slate-300 mb-8 leading-relaxed">
                            Welcome to Infinite BZ. These Terms and Conditions constitute a legally binding agreement made between you, whether personally or on behalf of an entity ("you") and Infinite BZ ("we", "us" or "our"), concerning your access to and use of our desktop web application and related services.
                        </p>

                        <div className="bg-slate-900/50 rounded-xl p-6 border border-white/5 mb-10">
                            <h3 className="flex items-center gap-2 text-sm font-bold text-slate-200 uppercase tracking-wider mb-4">
                                <FileText size={16} className="text-sky-500" />
                                Table of Contents
                            </h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {['User Responsibilities', 'Acceptable Use', 'Intellectual Property', 'Disclaimers', 'Limitation of Liability', 'Termination'].map((item, i) => (
                                    <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group">
                                        <span className="w-5 h-5 rounded flex items-center justify-center bg-slate-800 text-xs text-slate-400 font-mono group-hover:text-white transition-colors">{i + 1}</span>
                                        <span className="text-sm text-slate-400 group-hover:text-white transition-colors">{item}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-12">
                            <section>
                                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-3">
                                    <span className="text-sky-500">1.</span> User Responsibilities
                                </h3>
                                <div className="space-y-4 text-slate-400 leading-relaxed">
                                    <p>By using Infinite BZ, you agree to provide accurate, current, and complete information during the registration process and to update such information to keep it accurate, current, and complete.</p>
                                    <p>You are responsible for safeguarding your password and for all activities that occur under your account. You agree to notify us immediately of any unauthorized use of your account or any other breach of security.</p>
                                </div>
                            </section>

                            <section>
                                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-3">
                                    <span className="text-sky-500">2.</span> Acceptable Use
                                </h3>
                                <div className="space-y-4 text-slate-400 leading-relaxed">
                                    <p>You agree not to use the Service for any unlawful purpose or in any way that interrupts, damages, impairs, or renders the Service less efficient.</p>
                                    <ul className="list-disc pl-5 space-y-2 marker:text-slate-600">
                                        <li>Do not attempt to reverse engineer any part of the Service.</li>
                                        <li>Do not use automated systems or software to extract data (scraping).</li>
                                        <li>Do not harass, abuse, or harm another person or entity.</li>
                                    </ul>
                                </div>
                            </section>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export function PrivacyModal({ onClose }) {
    return (
        <div className="fixed inset-0 z-[100] bg-slate-950/90 backdrop-blur-sm flex items-center justify-end animate-in fade-in duration-200">
            {/* Click outside to close */}
            <div className="absolute inset-0" onClick={onClose} />

            {/* Slide-over Panel */}
            <div className="relative w-full max-w-2xl h-full bg-[#0B1221] border-l border-white/10 shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
                {/* Header */}
                <div className="flex items-center justify-between px-8 py-6 border-b border-white/5 bg-[#0B1221]">
                    <div className="flex items-center gap-2 text-slate-400 text-sm font-medium">
                        <Shield size={16} />
                        <span>Transparency & Trust</span>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/10 rounded-full text-slate-400 hover:text-white transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                    <div className="prose prose-invert prose-sm max-w-none">
                        <span className="inline-block py-1 px-2 rounded bg-sky-500/10 text-sky-400 text-xs font-bold uppercase tracking-wider mb-4">
                            Legal Documentation
                        </span>
                        <h1 className="text-4xl font-bold text-white mb-6">Privacy Policy</h1>

                        <p className="text-lg text-slate-300 mb-10 leading-relaxed border-l-4 border-sky-500 pl-6">
                            Your privacy is important to us. This policy outlines how Infinite BZ collects, uses, and protects your data while you use our event aggregation and auto-registration services.
                        </p>

                        <div className="grid gap-6">
                            <div className="bg-slate-900 rounded-xl p-6 border border-white/5 hover:border-sky-500/30 transition-colors">
                                <div className="w-10 h-10 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-500 mb-4">
                                    <FileText size={20} />
                                </div>
                                <h3 className="text-lg font-bold text-white mb-3">1. Information We Collect</h3>
                                <p className="text-slate-400 text-sm leading-relaxed mb-4">
                                    To provide our event aggregation and auto-registration services, we collect the following types of information:
                                </p>
                                <div className="grid sm:grid-cols-2 gap-4">
                                    <div className="bg-[#0B1221] p-4 rounded-lg">
                                        <h4 className="text-white font-semibold text-xs mb-2">Personal Identity</h4>
                                        <p className="text-slate-500 text-xs">Name, email address, phone number, and professional title required for event registration.</p>
                                    </div>
                                    <div className="bg-[#0B1221] p-4 rounded-lg">
                                        <h4 className="text-white font-semibold text-xs mb-2">Preferences</h4>
                                        <p className="text-slate-500 text-xs">Topics of interest, preferred locations (e.g., Chennai), and dietary restrictions for events.</p>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-slate-900 rounded-xl p-6 border border-white/5 hover:border-purple-500/30 transition-colors">
                                <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-500 mb-4">
                                    <Shield size={20} />
                                </div>
                                <h3 className="text-lg font-bold text-white mb-3">2. How We Use Your Data</h3>
                                <ul className="space-y-3">
                                    <li className="flex gap-3 text-sm text-slate-400">
                                        <div className="mt-1 w-1.5 h-1.5 rounded-full bg-sky-500 shrink-0" />
                                        <span><strong className="text-slate-200">Service Provision:</strong> To curate a personalized feed of tech meetups in Chennai and surrounding areas.</span>
                                    </li>
                                    <li className="flex gap-3 text-sm text-slate-400">
                                        <div className="mt-1 w-1.5 h-1.5 rounded-full bg-sky-500 shrink-0" />
                                        <span><strong className="text-slate-200">Auto-Registration:</strong> To automatically register you for free events you select, using your stored profile details so you don't have to fill forms repeatedly.</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
