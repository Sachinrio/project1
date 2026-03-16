import React from 'react';
import { Layers, Zap, Users, Globe } from 'lucide-react';

const HIGHLIGHTS = [
    {
        title: 'Multi-Source Sync',
        desc: 'Aggregated intelligence from Eventbrite, Meetup, and Chennai Trade Centre in a single feed.',
        icon: <Layers className="w-6 h-6" />
    },
    {
        title: 'Live Scrapping',
        desc: 'Our automated engines crawl thousands of data points daily to ensure zero missing opportunities.',
        icon: <Zap className="w-6 h-6" />
    },
    {
        title: 'Capital Network',
        desc: 'Direct bridge to VC nodes and angel networks active in the South Indian venture space.',
        icon: <Globe className="w-6 h-6" />
    },
    {
        title: 'Talent Hub',
        desc: 'Connect with core engineering and sales talent specifically filtered for the Chennai ecosystem.',
        icon: <Users className="w-6 h-6" />
    }
];

export const EcosystemHighlights = () => {
    return (
        <section className="py-4 relative overflow-hidden">
            {/* Subtle background effects */}
            <div className="absolute top-1/4 left-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none"></div>
            <div className="absolute bottom-1/4 right-0 w-96 h-96 bg-purple-500/5 rounded-full blur-[120px] pointer-events-none"></div>

            <div className="max-w-7xl mx-auto px-4 relative z-10">
                <div className="text-center mb-6">
                    <h2 className="text-sm font-black text-indigo-500 uppercase tracking-[0.3em] mb-4">Why Infinite BZ?</h2>
                    <h3 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight mb-6 leading-tight">
                        One Hub. <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Infinite Impact.</span>
                    </h3>
                    <p className="text-slate-500 max-w-2xl mx-auto font-medium">
                        The ultimate destination for founders, investors, and talent. We bridge the gap between fragmented data and strategic networking.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {HIGHLIGHTS.map((item, idx) => (
                        <div
                            key={idx}
                            className="bg-white/50 backdrop-blur-sm p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-2xl hover:shadow-indigo-500/10 hover:-translate-y-2 transition-all duration-500 group"
                        >
                            <div className="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center text-indigo-600 mb-8 group-hover:bg-indigo-600 group-hover:text-white transition-all duration-500 group-hover:rotate-6 group-hover:scale-110">
                                {item.icon}
                            </div>
                            <h4 className="text-xl font-black text-slate-900 mb-3 group-hover:text-indigo-600 transition-colors uppercase tracking-tight">{item.title}</h4>
                            <p className="text-slate-500 text-sm leading-relaxed font-medium">
                                {item.desc}
                            </p>

                            <div className="mt-8 pt-6 border-t border-slate-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                                <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em]">Learn More →</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
