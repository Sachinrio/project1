import { motion } from 'framer-motion';
import { Type, List, Ticket, MapPin, Check } from 'lucide-react';

export default function ProgressBar({ currentStep, totalSteps = 5 }) {
    const steps = [
        { id: 1, label: "Essentials", icon: Type },
        { id: 2, label: "Content", icon: List },
        { id: 3, label: "Tickets", icon: Ticket },
        { id: 4, label: "Venue", icon: MapPin },
        { id: 5, label: "Review", icon: Check },
    ];

    return (
        <div className="w-full max-w-3xl mx-auto px-4">
            <div className="relative flex items-center justify-between">
                {/* Background Line */}
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-white/10 rounded-full z-0" />

                {/* Active Line Progress */}
                <motion.div
                    className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full z-0 origin-left"
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: (currentStep - 1) / (totalSteps - 1) }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                    style={{ width: "100%" }}
                />

                {/* Steps */}
                {steps.map((s, index) => {
                    const isActive = currentStep >= s.id;
                    const isCurrent = currentStep === s.id;
                    const Icon = s.icon;

                    return (
                        <div key={s.id} className="relative z-10 flex flex-col items-center">
                            <motion.div
                                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors duration-300 ${isActive ? 'bg-[#1a1a1a] border-indigo-500 text-indigo-400' : 'bg-[#1a1a1a] border-white/10 text-slate-600'}`}
                                animate={{
                                    scale: isCurrent ? 1.2 : 1,
                                    boxShadow: isCurrent ? "0 0 20px rgba(99, 102, 241, 0.4)" : "none"
                                }}
                            >
                                <Icon size={16} />
                            </motion.div>

                            <motion.span
                                className={`absolute top-12 text-[10px] font-bold uppercase tracking-wider whitespace-nowrap ${isActive ? 'text-indigo-300' : 'text-slate-600'}`}
                                animate={{ opacity: isActive ? 1 : 0.5, y: isCurrent ? 0 : 0 }}
                            >
                                {s.label}
                            </motion.span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
