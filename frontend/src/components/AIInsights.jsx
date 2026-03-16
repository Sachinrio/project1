
import React, { useState, useEffect } from 'react';
import { GoogleGenAI } from "@google/genai";

export const AIInsights = () => {
    const [insight, setInsight] = useState("");
    const [displayText, setDisplayText] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    const fetchAIInsight = async () => {
        setIsLoading(true);
        setInsight("");
        setDisplayText("");
        try {
            const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
            const response = await ai.models.generateContent({
                model: 'gemini-3-flash-preview',
                contents: "Give me one sharp, ultra-specific business opportunity in Chennai this week. Mention a specific hub like OMR, Guindy, or ECR. Max 25 words.",
                config: {
                    systemInstruction: "You are 'Infinite BZ AI', the premier intelligence engine for Chennai's business ecosystem. You provide exclusive, high-value, and actionable market insights for founders and investors.",
                    temperature: 0.9,
                    topK: 1
                }
            });
            setInsight(response.text || "Deep-tech founders in Guindy are seeking seed capital. Connect with the Industrial Corridor node for early access.");
        } catch (error) {
            setInsight("SaaS valuations in Chennai's OMR belt are trending up. Focus on B2B AI vertical integrations for maximum investor interest.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchAIInsight();
    }, []);

    useEffect(() => {
        if (insight && displayText.length < insight.length) {
            const timeout = setTimeout(() => {
                setDisplayText(insight.slice(0, displayText.length + 1));
            }, 25);
            return () => clearTimeout(timeout);
        }
    }, [insight, displayText]);

    return (
        <div className="relative group">
            {/* Decorative Blur */}
            <div className="absolute -top-10 -left-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-[80px] pointer-events-none group-hover:bg-indigo-500/20 transition-all duration-1000"></div>

            <div className="glass-card p-10 rounded-[3rem] border-indigo-100/30 overflow-hidden relative z-10 transition-all hover:scale-[1.02] hover:rotate-1">
                {/* Animated Scanning Beam */}
                {isLoading && <div className="scan-beam"></div>}

                <div className="flex items-center justify-between mb-10">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-slate-900 rounded-[1.2rem] flex items-center justify-center text-white shadow-2xl group-hover:rotate-12 transition-transform relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500/20 to-transparent"></div>
                            <svg className="w-7 h-7 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                        </div>
                        <div>
                            <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500 mb-1">Infinite BZ AI</h4>
                            <h3 className="text-xl font-black text-slate-900 tracking-tight">Daily Alpha</h3>
                        </div>
                    </div>
                    <div className="flex gap-1.5">
                        {[1, 2, 3].map(i => (
                            <span
                                key={i}
                                className={`w-2 h-2 rounded-full transition-all duration-500 ${isLoading ? 'bg-indigo-500 animate-pulse' : 'bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.5)]'}`}
                                style={{ animationDelay: `${i * 0.2}s` }}
                            ></span>
                        ))}
                    </div>
                </div>

                <div className="min-h-[120px] font-medium text-lg text-slate-700 leading-relaxed">
                    {isLoading ? (
                        <div className="space-y-4">
                            <div className="h-4 w-full bg-slate-100 rounded-full animate-pulse"></div>
                            <div className="h-4 w-5/6 bg-slate-100 rounded-full animate-pulse"></div>
                            <div className="h-4 w-4/6 bg-slate-100 rounded-full animate-pulse"></div>
                        </div>
                    ) : (
                        <div className="relative">
                            <span className="text-6xl font-black text-indigo-500/10 absolute -top-10 -left-6 pointer-events-none select-none">“</span>
                            <p className="relative z-10 leading-[1.6] pl-2">
                                {displayText}
                                <span className="inline-block w-2.5 h-6 bg-indigo-500 animate-pulse ml-2 align-middle rounded-full shadow-[0_0_12px_rgba(79,70,229,0.5)]"></span>
                            </p>
                        </div>
                    )}
                </div>

                <button
                    onClick={fetchAIInsight}
                    disabled={isLoading}
                    className="mt-10 w-full py-5 bg-slate-50 border border-slate-100 rounded-[1.5rem] text-[11px] font-black uppercase tracking-[0.2em] text-slate-400 hover:bg-indigo-600 hover:text-white hover:border-indigo-600 hover:shadow-xl hover:shadow-indigo-200 transition-all duration-500 disabled:opacity-50 btn-bounce relative group/btn"
                >
                    <span className="relative z-10">
                        {isLoading ? 'Scanning Chennai Nodes...' : 'Fetch New Intel'}
                    </span>
                    <div className="absolute inset-0 bg-indigo-700 rounded-[1.5rem] scale-x-0 group-hover/btn:scale-x-100 transition-transform origin-left -z-0"></div>
                </button>
            </div>
        </div>
    );
};
