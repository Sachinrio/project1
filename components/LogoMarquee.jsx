import React from 'react';

const LOGOS = [
    { name: 'ZOHO', color: 'text-slate-800' },
    { name: 'FRESHWORKS', color: 'text-slate-800' },
    { name: 'TCS', color: 'text-slate-800' },
    { name: 'IIT MADRAS', color: 'text-slate-800' },
    { name: 'HCL TECH', color: 'text-slate-800' },
    { name: 'TENSORFLOW', color: 'text-slate-800' },
    { name: 'Y COMBINATOR', color: 'text-orange-500' }, // Just for variety
    { name: 'SAASBOOMi', color: 'text-slate-800' },
];

export const LogoMarquee = () => {
    return (
        <div className="w-full relative overflow-hidden py-10 opacity-50 hover:opacity-100 transition-opacity duration-500 group">
            {/* Gradient Masks for fade effect */}
            <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-[#fdfdff] to-transparent z-10"></div>
            <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-[#fdfdff] to-transparent z-10"></div>

            <div className="flex w-max animate-marquee gap-20 group-hover:[animation-play-state:paused]">
                {[...LOGOS, ...LOGOS, ...LOGOS].map((logo, idx) => (
                    <div key={idx} className="flex items-center gap-2 grayscale hover:grayscale-0 transition-all duration-300">
                        {/* We can replace this with actual SVGs later. For now, premium typography. */}
                        <span className={`text-xl font-black tracking-widest ${logo.color} whitespace-nowrap`}>
                            {logo.name}
                        </span>
                    </div>
                ))}
            </div>

            <style jsx>{`
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-33.33%); }
        }
        .animate-marquee {
          animation: marquee 40s linear infinite;
        }
      `}</style>
        </div>
    );
};
