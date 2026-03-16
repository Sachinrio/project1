
import React from 'react';

export const CTASection = ({ onLogin, onSignup }) => {
    return (
        <section className="bg-slate-900 py-10">
            <div className="max-w-7xl mx-auto px-4 text-center">
                <div className="inline-block px-4 py-1.5 rounded-full bg-teal-500/10 text-teal-400 text-sm font-bold tracking-widest uppercase mb-6">
                    Growth Engine
                </div>
                <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-8">
                    Ready to Accelerate Your <br /> Business Growth?
                </h2>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <button
                        onClick={onLogin}
                        className="bg-teal-500 hover:bg-teal-400 text-white px-8 py-4 rounded-full font-bold text-lg shadow-xl shadow-teal-500/20 transition-all active:scale-95"
                    >
                        Join Free - No Credit Card Needed
                    </button>
                    <button
                        onClick={onSignup}
                        className="bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-full font-bold text-lg backdrop-blur-sm border border-white/20 transition-all active:scale-95"
                    >
                        Schedule a Demo
                    </button>
                </div>

                <p className="mt-8 text-slate-400 text-sm">
                    The heartbeat of Chennai’s startup & business ecosystem.
                </p>
            </div>
        </section>
    );
};
