import React from 'react';

const TESTIMONIALS = [
    { name: 'Arjun V.', role: 'CEO @ TechScale', quote: 'IBZ is where we found our series A lead. The network quality is unparalleled in Chennai.' },
    { name: 'Priya R.', role: 'Founder @ GreenFin', quote: 'The AI matches are eerily accurate. I connected with my co-founder here in just 2 days.' },
    { name: 'Sameer K.', role: 'Partner @ Apex Ventures', quote: 'A goldmine for early-stage deal flow. The OMR summits are a must-attend for any investor.' },
    { name: 'Lakshmi N.', role: 'CTO @ DataWave', quote: 'Comparing this to other hubs, the signal-to-noise ratio here is incredibly high.' },
    { name: 'Vikram S.', role: 'Director @ StartTN', quote: 'Exactly what the ecosystem needed. A centralized, high-quality professional hub.' },
    { name: 'Ananya M.', role: 'Product Lead @ Zoho', quote: 'Found amazing talent for our new AI division through the talent matching feature.' },
];

const TestimonialCard = ({ data }) => (
    <div className="glass p-8 rounded-[2rem] relative group border border-white/10 hover:border-indigo-500/30 transition-colors bg-slate-900/50 backdrop-blur-md mb-6 w-full break-inside-avoid">
        <div className="text-4xl text-indigo-500/20 font-black absolute top-6 left-6 pointer-events-none">“</div>
        <p className="text-slate-300 mb-6 leading-relaxed italic relative z-10 text-sm">
            {data.quote}
        </p>
        <div className="flex items-center gap-3 border-t border-white/5 pt-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs ring-2 ring-white/10">
                {data.name.charAt(0)}
            </div>
            <div>
                <h4 className="font-bold text-white text-xs">{data.name}</h4>
                <p className="text-indigo-400 text-[10px] font-bold uppercase tracking-wider">{data.role}</p>
            </div>
        </div>
    </div>
);

const MarqueeColumn = ({ items, duration = "40s", reverse = false }) => (
    <div className="relative flex flex-col gap-6 overflow-hidden h-[800px] w-full group">
        {/* Vertical Gradient Masks */}
        <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-[#fdfdff] to-transparent z-10"></div>
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#fdfdff] to-transparent z-10"></div>

        <div
            className={`flex flex-col gap-6 animate-marquee-y ${reverse ? 'direction-reverse' : ''} group-hover:[animation-play-state:paused]`}
            style={{ animationDuration: duration }}
        >
            {[...items, ...items, ...items].map((t, i) => (
                <TestimonialCard key={i} data={t} />
            ))}
        </div>

        <style jsx>{`
      @keyframes marquee-y {
        0% { transform: translateY(0); }
        100% { transform: translateY(-33.33%); }
      }
      .animate-marquee-y {
        animation: marquee-y linear infinite;
      }
      .direction-reverse {
        animation-direction: reverse;
      }
    `}</style>
    </div>
);

export const Testimonials = () => {
    return (
        <section className="py-24 relative overflow-hidden">
            {/* Background blobs for depth */}
            <div className="absolute top-1/4 left-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-[120px]"></div>
            <div className="absolute bottom-1/4 right-0 w-96 h-96 bg-purple-500/5 rounded-full blur-[120px]"></div>

            <div className="max-w-7xl mx-auto px-4 relative z-10">
                <div className="text-center mb-20">
                    <h2 className="text-sm font-black text-indigo-500 uppercase tracking-[0.3em] mb-4">Community Voices</h2>
                    <h3 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight mb-6">
                        Trusted by the <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Visionaries.</span>
                    </h3>
                    <p className="text-slate-500 max-w-2xl mx-auto">
                        Join thousands of founders and investors building the future of Chennai's ecosystem.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 h-[600px] overflow-hidden mask-image-gradient">
                    <MarqueeColumn items={TESTIMONIALS.slice(0, 3)} duration="45s" />
                    <MarqueeColumn items={TESTIMONIALS.slice(2, 5)} duration="55s" reverse />
                    <MarqueeColumn items={TESTIMONIALS.slice(1, 4)} duration="50s" />
                </div>
            </div>
        </section>
    );
};
