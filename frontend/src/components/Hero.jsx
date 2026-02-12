import { LogoMarquee } from './LogoMarquee';
import { MagneticButton } from './MagneticButton';
import { MouseSpotlight } from './MouseSpotlight';
import { CyclingText } from './CyclingText';
import { ThreeBackground } from './ThreeBackground';

const AnimatedText = ({ text, baseDelay = 0, className = "", useGradient = false }) => {
    return (
        <span className={className}>
            {text.split('').map((char, i) => (
                <span
                    key={i}
                    className="animate-letter inline-block" // Changed to inline-block for proper spacing
                    style={{ animationDelay: `${baseDelay + i * 0.03}s` }}
                >
                    <span className={useGradient ? 'text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-blue-600 to-emerald-500 animate-gradient-text' : ''}>
                        {char === ' ' ? '\u00A0' : char}
                    </span>
                </span>
            ))}
        </span>
    );
};

export const Hero = ({ events = [], onLogin, onExplore }) => {
    return (
        <section className="relative pt-2 pb-10">
            <MouseSpotlight />
            <ThreeBackground />

            {/* Dynamic Background Elements - Animated */}
            <div className="absolute -top-24 -left-24 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] floating-orb"></div>
            <div className="absolute top-1/2 -right-24 w-80 h-80 bg-emerald-500/10 rounded-full blur-[100px] floating-orb" style={{ animationDelay: '-5s' }}></div>
            <div className="absolute bottom-0 left-1/4 w-64 h-64 bg-cyan-500/5 rounded-full blur-[80px] floating-orb" style={{ animationDelay: '-8s' }}></div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="max-w-4xl mx-auto text-center mb-16">


                    {/* Hero Video - Seamless Integration */}
                    <div className="relative w-full max-w-2xl mx-auto mb-0 mt-4 group">
                        {/* Sticker: Left of Video - Maximized Size & Repositioned for Smaller Video */}
                        <div className="hidden md:block absolute -left-[35rem] top-[20%] -translate-y-1/2 w-[55rem] animate-float-v z-20 pointer-events-none">
                            <img src="/media/left-float-gemini.png" alt="Sticker Left" className="w-full h-auto drop-shadow-xl rotate-[-6deg]" />
                        </div>
                        {/* Sticker: Right of Video - Maximized Size & Repositioned for Smaller Video */}
                        <div className="hidden md:block absolute -right-[35rem] top-[20%] -translate-y-1/2 w-[55rem] animate-float-v z-20 pointer-events-none">
                            <img src="/media/right-float-gemini.png" alt="Sticker Right" className="w-full h-auto drop-shadow-xl rotate-[6deg]" />
                        </div>
                        {/* Video Layer Container */}
                        <div className="relative rounded-[1.2rem] shadow-2xl overflow-hidden bg-[#fdfdff] border border-white/20 aspect-video w-full">
                            <video
                                autoPlay
                                loop
                                muted
                                playsInline
                                preload="auto"
                                onTimeUpdate={(e) => {
                                    const time = e.target.currentTime;
                                    const overlay = document.getElementById('video-overlay-text');
                                    if (overlay) {
                                        if (time >= 0.07 && time <= 3.0) {
                                            overlay.style.opacity = '1';
                                            overlay.style.transform = 'scale(1)';
                                        } else {
                                            overlay.style.opacity = '0';
                                            overlay.style.transform = 'scale(0.95)';
                                        }
                                    }
                                }}
                                className="w-full h-full object-cover aspect-video mix-blend-multiply dark:mix-blend-normal"
                            >
                                <source src="/hero-video-radial.mp4" type="video/mp4" />
                                Your browser does not support the video tag.
                            </video>

                            {/* Timed Overlay Text - Centered & Transparent Background */}
                            <div
                                id="video-overlay-text"
                                className="absolute inset-0 flex items-center justify-center px-6 opacity-0 scale-[0.95] transition-all duration-300 ease-out z-30 pointer-events-none"
                            >
                                <div className="text-center">
                                    <p className="text-xl md:text-4xl font-black text-slate-900 tracking-tight leading-tight">
                                        Creating <span className="text-indigo-600">boundless</span> networking opportunities for everyone
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <h1 className="text-3xl md:text-6xl font-black text-slate-900 mb-8 leading-[1.2] tracking-tight relative z-20" style={{ perspective: '1200px' }}>
                        <AnimatedText text="Discovery for the" baseDelay={0.2} className="block" />

                        {/* Replaced static Infinite Minded with Cycling Text */}
                        <div className="h-[1.2em] relative flex justify-center">
                            <CyclingText />
                        </div>
                    </h1>

                    <p className="text-xl text-slate-500 font-medium max-w-2xl mx-auto leading-relaxed">
                        Connect with Chennai’s most dynamic network of innovators. The ultimate gateway to business growth, strategic partnerships, and infinite opportunities.
                    </p>
                </div>

                {/* CTA Buttons with Magnetic Effect */}
                <div className="flex flex-col sm:flex-row items-center justify-center gap-6 relative z-20">
                    <MagneticButton strength={40}>
                        <button
                            onClick={onLogin}
                            className="bg-slate-900 hover:bg-slate-800 text-white text-lg font-bold px-10 py-4 rounded-xl shadow-lg shadow-slate-900/20 transition-all hover:scale-105 btn-bounce flex items-center gap-2 group"
                        >
                            Login Hub
                            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                            </svg>
                        </button>
                    </MagneticButton>

                    <MagneticButton strength={40}>
                        <button
                            onClick={onExplore}
                            className="bg-white text-slate-700 hover:text-indigo-600 text-lg font-bold px-10 py-4 rounded-xl border border-slate-200 hover:border-indigo-100 shadow-sm hover:shadow-md transition-all hover:scale-105 btn-bounce"
                        >
                            Explore Events
                        </button>
                    </MagneticButton>
                </div>

                {/* Logo Marquee & Bottom Floating Images */}
                <div className="mt-10 pt-8 border-t border-slate-100 relative z-10">
                    <p className="text-center text-xs font-bold text-slate-400 uppercase tracking-widest mb-8">Aggregated from Top Sources</p>



                    {/* ORIGINAL Bottom Floating Images - Marquee Level */}
                    <div className="hidden xl:block absolute -left-10 -bottom-60 w-[24rem] animate-float-v z-20 pointer-events-none" style={{ animationDelay: '1s' }}>
                        <img
                            src="/media/left-float-hq.png"
                            alt="Business Growth"
                            className="w-full h-auto drop-shadow-2xl"
                        />
                    </div>

                    <div className="hidden xl:block absolute -right-8 -bottom-60 w-[24rem] animate-float-v z-20 pointer-events-none" style={{ animationDelay: '2.5s' }}>
                        <img
                            src="/media/right-float-hq.png"
                            alt="Deal Signed"
                            className="w-full h-auto drop-shadow-2xl"
                        />
                    </div>

                    <LogoMarquee events={events} />
                </div>
            </div>
        </section>
    );
};
const FilterChip = ({ label, active }) => (
    <button className={`px-6 py-2.5 rounded-2xl text-xs font-black uppercase tracking-widest transition-all btn-bounce border ${active ? 'bg-slate-900 border-slate-900 text-white shadow-lg' : 'bg-white border-slate-100 text-slate-500 hover:border-indigo-200 hover:text-indigo-600'
        }`}>
        {label}
    </button>
);
