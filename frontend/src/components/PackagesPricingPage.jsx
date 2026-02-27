import React, { useState } from 'react';
import { Check, Plus, Code, Target, Shield, Briefcase, FileText, ShoppingBag, Globe, Download, DollarSign, Activity, ArrowLeft } from 'lucide-react';
import QuoteGeneratorModal from './QuoteGeneratorModal';

const PackagesPricingPage = ({ onNavigate }) => {
    const [isQuoteOpen, setIsQuoteOpen] = useState(false);
    const [selectedAddons, setSelectedAddons] = useState([]);

    const packages = [
        {
            name: "Basic",
            tier: "Starter",
            tagline: "Company legally incorporated and operational. The foundation.",
            price: "15,000",
            range: "to ₹22,000 + 18% GST • Govt fees extra at actuals",
            color: "cyan",
            features: [
                "Entity Selection Consulting",
                "DSC & DIN",
                "Name Approval (RUN/SPICe+)",
                "Incorporation Filing (SPICe+)",
                "PAN & TAN",
                "Statutory Auditor Appointment"
            ],
            missing: [],
            delivery: "15-20 business days"
        },
        {
            name: "Growth",
            tier: "Growth",
            tagline: "Full setup — banking, GST, MSME. Ready to trade from Day 1.",
            price: "28,000",
            range: "to ₹38,000 + 18% GST • Govt fees extra at actuals",
            color: "indigo",
            features: [
                "Entity Selection Consulting",
                "DSC & DIN",
                "Name Approval (RUN/SPICe+)",
                "Incorporation Filing (SPICe+)",
                "PAN & TAN",
                "Bank Account Setup",
                "GST Registration",
                "MSME / Udyam Registration",
                "Professional Tax (Tamil Nadu)",
                "Statutory Auditor Appointment",
                "Compliance Calendar Creation"
            ],
            missing: [],
            delivery: "25-35 business days"
        },
        {
            name: "E-Com Pro",
            tier: "E-Commerce",
            tagline: "Full Amazon + D2C launch infrastructure. The most popular.",
            price: "55,000",
            range: "to ₹80,000 + 18% GST • Govt fees extra at actuals",
            color: "fuchsia",
            highlight: true,
            features: [
                "Entity Selection Consulting",
                "DSC & DIN",
                "Name Approval (RUN/SPICe+)",
                "Incorporation Filing (SPICe+)",
                "PAN & TAN",
                "Bank Account Setup",
                "GST Registration",
                "MSME / Udyam Registration",
                "Startup India (DPIIT)",
                "Professional Tax (Tamil Nadu)",
                "Statutory Auditor Appointment",
                "Shop & Establishment",
                "Amazon/Flipkart Seller Setup",
                "Payment Gateway Integration",
                "Website & Domain Setup",
                "Compliance Calendar Creation"
            ],
            missing: [],
            delivery: "40-55 business days"
        },
        {
            name: "Complete Launch",
            tier: "All-in-One",
            tagline: "All 20 services + 3 months free retainer. The complete OS.",
            price: "95,000",
            range: "to ₹1,50,000 + 18% GST • Govt fees extra at actuals",
            color: "emerald",
            features: [
                "Entity Selection Consulting",
                "DSC & DIN",
                "Name Approval (RUN/SPICe+)",
                "Incorporation Filing (SPICe+)",
                "PAN & TAN",
                "Bank Account Setup",
                "GST Registration",
                "MSME / Udyam Registration",
                "Startup India (DPIIT)",
                "EPF & ESIC Registration",
                "Professional Tax (Tamil Nadu)",
                "Statutory Auditor Appointment",
                "Shop & Establishment",
                "IEC (Import Export Code)",
                "FSSAI License",
                "Amazon/Flipkart Seller Setup",
                "Payment Gateway Integration",
                "Website & Domain Setup",
                "Compliance Calendar Creation",
                "Ongoing ROC / GST Retainer"
            ],
            missing: [],
            delivery: "55-70 business days"
        }
    ];

    const margins = [
        { pkg: "Basic", price: "₹15,000—₹22,000", govt: "₹4,000—₹8,000", rev: "₹10,000—₹14,000", margin: "45-50%", color: "cyan", delivery: "15-20 days" },
        { pkg: "Growth", price: "₹28,000—₹38,000", govt: "₹6,000—₹10,000", rev: "₹20,000—₹28,000", margin: "42-48%", color: "indigo", delivery: "25-35 days" },
        { pkg: "E-Com Pro", price: "₹55,000—₹80,000", govt: "₹8,000—₹15,000", rev: "₹42,000—₹58,000", margin: "48-55%", color: "fuchsia", delivery: "40-55 days" },
        { pkg: "Complete", price: "₹95,000—₹1,50,000", govt: "₹15,000—₹25,000", rev: "₹72,000—₹1,12,000", margin: "50-60%", color: "emerald", delivery: "55-70 days" }
    ];

    const addons = [
        { name: "Trademark Registration", price: "₹8,000-15,000", icon: <Shield size={18} className="text-cyan-600" />, iconBg: "bg-cyan-100" },
        { name: "Amazon PPC Management", price: "₹8,000-20,000/mo", icon: <Target size={18} className="text-indigo-600" />, iconBg: "bg-indigo-100" },
        { name: "WooCommerce Store", price: "₹20,000-50,000", icon: <ShoppingBag size={18} className="text-fuchsia-600" />, iconBg: "bg-fuchsia-100" },
        { name: "ITR Filing (Co + Directors)", price: "₹5,000-15,000", icon: <FileText size={18} className="text-blue-600" />, iconBg: "bg-blue-100" },
        { name: "FSSAI Annual Renewal", price: "₹2,000-5,000", icon: <Globe size={18} className="text-purple-600" />, iconBg: "bg-purple-100" },
        { name: "GST LUT Filing (Exporters)", price: "₹2,000", icon: <Download size={18} className="text-rose-600" />, iconBg: "bg-rose-100" },
        { name: "Director Change (ROC)", price: "₹5,000-8,000", icon: <Activity size={18} className="text-violet-600" />, iconBg: "bg-violet-100" },
        { name: "Annual ROC Filing", price: "₹8,000-15,000", icon: <Briefcase size={18} className="text-emerald-600" />, iconBg: "bg-emerald-100" },
        { name: "Payroll Processing", price: "₹3,000-8,000/mo", icon: <DollarSign size={18} className="text-teal-600" />, iconBg: "bg-teal-100" },
        { name: "D2C Brand Consulting", price: "₹15,000-25,000", icon: <Code size={18} className="text-pink-600" />, iconBg: "bg-pink-100" }
    ];

    return (
        <div className="min-h-screen font-sans text-slate-900 relative overflow-hidden bg-[#fafcff]">
            {/* Premium Dynamic Background */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-gradient-to-br from-indigo-500/10 to-purple-500/10 blur-[100px]"></div>
                <div className="absolute top-[40%] right-[-10%] w-[40%] h-[40%] rounded-full bg-gradient-to-l from-fuchsia-500/10 to-pink-500/10 blur-[100px]"></div>
                <div className="absolute bottom-[-10%] left-[20%] w-[60%] h-[60%] rounded-full bg-gradient-to-tr from-cyan-500/10 to-emerald-500/10 blur-[100px]"></div>
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_0%,#000_70%,transparent_100%)]"></div>
                <div className="absolute inset-0 opacity-[0.15] mix-blend-overlay" style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")` }}></div>
            </div>

            {/* Content Wrapper */}
            <div className="relative z-10 pb-20">
                {/* Top Navigation Bar / Header */}
                <div className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-fuchsia-100/50 px-8 py-4 flex justify-between items-center mb-0">
                    <div className="flex items-center gap-6">
                        <button
                            onClick={() => onNavigate('landing')}
                            className="flex items-center gap-2 text-slate-500 hover:text-indigo-600 transition-colors font-bold text-sm"
                        >
                            <ArrowLeft size={18} /> Back
                        </button>
                        <div
                            className="cursor-pointer flex items-center gap-2 group"
                            onClick={() => onNavigate('landing')}
                        >
                            <div className="text-2xl font-black tracking-tighter text-slate-900 group-hover:text-indigo-600 transition-colors">IBZ</div>
                        </div>
                    </div>
                    <div className="flex-1 flex justify-center items-center">
                        {/* Centered area cleared as requested */}
                    </div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => setIsQuoteOpen(true)}
                            className="flex items-center gap-2 px-5 py-2 border border-slate-200 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
                        >
                            <Code size={16} /> Quote Generator
                        </button>
                    </div>
                </div>

                <div className="max-w-7xl mx-auto px-6 pt-16">

                    <div className="mb-16">
                        <h2 className="text-5xl font-black text-slate-900 mb-6 tracking-tight">Package <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-fuchsia-600">Structure</span> & Pricing</h2>
                        <p className="text-slate-500 text-xl font-medium max-w-3xl leading-relaxed">
                            Modular, tiered packages designed for the Chennai market. All prices in INR + 18% GST. Government fees passed at actuals with zero markup.
                        </p>
                        <div className="w-full h-px bg-slate-200 mt-12"></div>
                    </div>

                    {/* Pricing Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-24 relative">
                        {packages.map((pkg, idx) => (
                            <div key={idx} className={`relative flex flex-col bg-white rounded-3xl p-8 border ${pkg.highlight ? 'border-fuchsia-500 shadow-2xl shadow-fuchsia-500/10 scale-105 z-10' : 'border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:-translate-y-1'} transition-all duration-300`}>
                                {/* Top decorative bar */}
                                <div className={`absolute top-0 left-8 right-8 h-1.5 rounded-b-xl ${pkg.color === 'cyan' ? 'bg-cyan-500' :
                                    pkg.color === 'indigo' ? 'bg-indigo-500' :
                                        pkg.color === 'fuchsia' ? 'bg-gradient-to-r from-fuchsia-500 to-purple-500' : 'bg-emerald-500'
                                    }`}></div>

                                {pkg.highlight && (
                                    <div className="absolute -top-3 right-6 bg-gradient-to-r from-fuchsia-600 to-purple-600 text-white text-[10px] font-black uppercase tracking-widest px-4 py-1.5 rounded-full shadow-lg shadow-fuchsia-600/30">
                                        Most Popular
                                    </div>
                                )}

                                <div className="mb-6 mt-2">
                                    <div className={`flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest mb-4 ${pkg.color === 'cyan' ? 'text-cyan-600' :
                                        pkg.color === 'indigo' ? 'text-indigo-600' :
                                            pkg.color === 'fuchsia' ? 'text-fuchsia-600' : 'text-emerald-600'
                                        }`}>
                                        <Target size={14} className="stroke-[2.5px]" /> {pkg.tier}
                                    </div>
                                    <h3 className="text-3xl font-black text-slate-900 mb-3 tracking-tight">{pkg.name}</h3>
                                    <p className="text-sm font-medium text-slate-500 leading-relaxed min-h-[40px]">{pkg.tagline}</p>
                                </div>

                                <div className="mb-8">
                                    <div className={`text-4xl font-black tracking-tight mb-1 ${pkg.color === 'cyan' ? 'text-cyan-700' :
                                        pkg.color === 'indigo' ? 'text-indigo-700' :
                                            pkg.color === 'fuchsia' ? 'text-fuchsia-700' : 'text-emerald-700'
                                        }`}>
                                        <span className="text-2xl mr-1 font-medium font-sans">₹</span>{pkg.price}
                                    </div>
                                    <p className="text-[10px] font-bold text-slate-400">{pkg.range}</p>
                                </div>

                                <div className="flex-grow flex flex-col mb-8 overflow-hidden relative">
                                    <h4 className={`text-xs font-black uppercase tracking-widest mb-4 ${pkg.color === 'cyan' ? 'text-cyan-600' :
                                        pkg.color === 'indigo' ? 'text-indigo-600' :
                                            pkg.color === 'fuchsia' ? 'text-fuchsia-600' : 'text-emerald-600'
                                        }`}>Services Provided</h4>

                                    <div className="relative w-full h-[250px] overflow-hidden flex-grow flex items-start justify-center">
                                        {/* Gradient masks for smooth fade in/out at edges */}
                                        <div className="absolute top-0 left-0 right-0 h-8 z-10 bg-gradient-to-b from-white to-transparent pointer-events-none"></div>
                                        <div className="absolute bottom-0 left-0 right-0 h-8 z-10 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>

                                        {/* Scrolling container */}
                                        <div className="flex flex-col animate-marquee hover:[animation-play-state:paused] cursor-default w-full">
                                            {/* First set of items */}
                                            {[...pkg.features, ...pkg.missing].filter(Boolean).map((feature, idx) => (
                                                <div key={`a-${idx}`} className="flex items-center px-2 py-2">
                                                    <span className={`w-1.5 h-1.5 rounded-full mr-3 shrink-0 ${pkg.features.includes(feature) ? (pkg.color === 'cyan' ? 'bg-cyan-500' : pkg.color === 'indigo' ? 'bg-indigo-500' : pkg.color === 'fuchsia' ? 'bg-fuchsia-500' : 'bg-emerald-500') : 'bg-slate-300'}`}></span>
                                                    <span className={`text-sm font-semibold tracking-wide ${pkg.features.includes(feature) ? 'text-slate-700' : 'text-slate-400 line-through decoration-slate-300'} whitespace-normal text-left`}>{feature}</span>
                                                </div>
                                            ))}
                                            {/* Duplicate set for seamless loop */}
                                            {[...pkg.features, ...pkg.missing].filter(Boolean).map((feature, idx) => (
                                                <div key={`b-${idx}`} className="flex items-center px-2 py-2">
                                                    <span className={`w-1.5 h-1.5 rounded-full mr-3 shrink-0 ${pkg.features.includes(feature) ? (pkg.color === 'cyan' ? 'bg-cyan-500' : pkg.color === 'indigo' ? 'bg-indigo-500' : pkg.color === 'fuchsia' ? 'bg-fuchsia-500' : 'bg-emerald-500') : 'bg-slate-300'}`}></span>
                                                    <span className={`text-sm font-semibold tracking-wide ${pkg.features.includes(feature) ? 'text-slate-700' : 'text-slate-400 line-through decoration-slate-300'} whitespace-normal text-left`}>{feature}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-auto pt-6 border-t border-slate-100 flex flex-col items-center">
                                    <button
                                        onClick={() => onNavigate('all-services', { tier: pkg.tier })}
                                        className={`w-full py-3.5 rounded-xl font-bold text-sm mb-3 transition-all ${pkg.highlight
                                            ? `bg-slate-900 hover:bg-black shadow-lg shadow-slate-900/20 hover:scale-[1.02] ${pkg.color === 'cyan' ? 'text-cyan-400' : pkg.color === 'indigo' ? 'text-indigo-400' : pkg.color === 'fuchsia' ? 'text-fuchsia-400' : 'text-emerald-400'}`
                                            : `bg-white border-2 border-slate-100 hover:border-black hover:bg-black hover:scale-[1.02] ${pkg.color === 'cyan' ? 'text-cyan-600 hover:text-cyan-400' : pkg.color === 'indigo' ? 'text-indigo-600 hover:text-indigo-400' : pkg.color === 'fuchsia' ? 'text-fuchsia-600 hover:text-fuchsia-400' : 'text-emerald-600 hover:text-emerald-400'}`
                                            }`}>
                                        Select {pkg.tier} &rarr;
                                    </button>
                                    <div className="text-[10px] font-bold text-slate-400 flex items-center gap-1.5 uppercase tracking-wider">
                                        <Clock size={12} className="stroke-[2.5px]" /> {pkg.delivery}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>



                    {/* Add-on Services Grid */}
                    <div className="mb-24">
                        <div className="flex items-center justify-center mb-8 relative">
                            <div className="absolute w-full h-px bg-slate-200"></div>
                            <h4 className="relative bg-[#fdfdff] px-6 text-xs font-black uppercase tracking-[0.15em] text-slate-400">Add-On Services</h4>
                        </div>

                        <div className="flex justify-between items-end mb-8">
                            <h3 className="text-2xl font-black text-slate-900 tracking-tight">Modular Add-Ons</h3>
                            <span className="bg-emerald-50 text-emerald-600 border border-emerald-100 text-xs font-black uppercase tracking-[0.1em] px-4 py-1.5 rounded-full">10 Available</span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                            {addons.map((add, idx) => {
                                const isActive = selectedAddons.includes(add.name);
                                return (
                                    <div key={idx}
                                        onClick={() => {
                                            if (isActive) {
                                                setSelectedAddons(selectedAddons.filter(item => item !== add.name));
                                            } else {
                                                setSelectedAddons([...selectedAddons, add.name]);
                                            }
                                        }}
                                        className={`flex items-center justify-between p-6 rounded-2xl border transition-all duration-300 cursor-pointer group ${isActive
                                            ? 'bg-white border-indigo-500 shadow-lg shadow-indigo-500/10 scale-[1.02]'
                                            : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-lg hover:shadow-slate-200/50 hover:scale-[1.01]'
                                            }`}>
                                        <div className="flex items-center gap-4">
                                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${add.iconBg} ${isActive ? 'ring-4 ring-indigo-50' : ''}`}>
                                                {add.icon}
                                            </div>
                                            <div>
                                                <h5 className={`font-bold text-sm mb-1 transition-colors ${isActive ? 'text-indigo-900' : 'text-slate-900 group-hover:text-indigo-600'}`}>{add.name}</h5>
                                                <p className={`text-xs font-black tracking-wide ${isActive ? 'text-indigo-600' : 'text-slate-500'}`}>{add.price}</p>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>

                </div>

                <QuoteGeneratorModal
                    isOpen={isQuoteOpen}
                    onClose={() => setIsQuoteOpen(false)}
                />
            </div>
        </div>
    );
};

function Clock({ size, className }) {
    return <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>
}

export default PackagesPricingPage;
