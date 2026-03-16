import React, { useState } from 'react';
import {
    Landmark, FileKey, CheckSquare, FileSignature, CreditCard, Building2,
    Calculator, FileSpreadsheet, Rocket, ShieldCheck, Briefcase, FileSearch,
    Store, Plane, HeartHandshake, ShoppingCart, Smartphone, Globe,
    CalendarCheck, Repeat, Plus, Code, ArrowLeft, Bot
} from 'lucide-react';
import QuoteGeneratorModal from './QuoteGeneratorModal';

const AllServicesPage = ({ onNavigate, selectedTier }) => {
    const [isQuoteOpen, setIsQuoteOpen] = useState(false);

    const tierMappings = {
        'Starter': ["01", "02", "03", "04", "05", "12"],
        'Growth': ["01", "02", "03", "04", "05", "06", "07", "08", "11", "12", "19"],
        'E-Commerce': ["01", "02", "03", "04", "05", "06", "07", "08", "09", "11", "12", "13", "16", "17", "18", "19"],
        'All-in-One': ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
    };

    // Define the base universe of services based on the selected package tier
    const baseServiceIds = selectedTier && tierMappings[selectedTier] ? tierMappings[selectedTier] : tierMappings['All-in-One'];

    // Dynamic text for the header based on selected package
    const headerText = {
        'Starter': {
            title: "Starter Package",
            highlight: "6 Services",
            description: "The foundational setup required to legally incorporate your company and begin basic operations."
        },
        'Growth': {
            title: "Growth Package",
            highlight: "11 Services",
            description: "Full business setup including banking, GST, and MSME registration. Get ready to trade from Day 1."
        },
        'E-Commerce': {
            title: "E-Com Pro Package",
            highlight: "16 Services",
            description: "Comprehensive infrastructure for Amazon & D2C launch, including payment gateways and website setup."
        },
        'All-in-One': {
            title: "Complete Launch",
            highlight: "20 Services",
            description: "The ultimate business operating system. All 20 services included with a 3-month free compliance retainer."
        }
    };

    // Default to 'All-in-One' text if no specific tier is selected or recognized
    const pageContent = (selectedTier && headerText[selectedTier]) ? headerText[selectedTier] : headerText['All-in-One'];

    // The active filter now strictly handles categories, not tier names
    const [activeFilter, setActiveFilter] = useState('All');
    const categories = ["Registration", "Tax & Compliance", "E-Commerce", "Licenses", "Retainer"];

    const services = [
        {
            id: "01", name: "Entity Selection Consulting", icon: <Landmark size={20} className="text-indigo-600" />, govt: "NIL", prof: "₹2,000-5,000", risk: "LOW", category: "Registration", riskColor: "emerald",
            sla: "2 business days",
            included: ["1-hour structured consultation (video/in-person)", "Comparative: Pvt Ltd vs OPC vs LLP vs Partnership", "Tax implication overview for each entity", "Liability & compliance burden comparison", "Written recommendation report", "E-commerce suitability assessment (Amazon/Flipkart)"],
            excluded: ["Legal opinion letter (separate engagement)", "Tax planning beyond scope", "Actual implementation of chosen entity"],
            documents: ["Director/Promoter PAN cards", "Nature of business description", "Expected Year 1 turnover", "Number of shareholders/partners", "Foreign investment plans (if any)"],
            riskNote: "Client may choose wrong entity due to incomplete disclosure — use detailed intake form"
        },
        {
            id: "02", name: "DSC & DIN", icon: <FileKey size={20} className="text-amber-600" />, govt: "₹1,500-2,000/DSC", prof: "₹500-1,000/DSC", risk: "LOW", category: "Registration", riskColor: "emerald",
            sla: "3-5 business days",
            included: ["Class 3 DSC for up to 2 directors", "DIN application through SPICe+ (DIR-3 if needed)", "Coordination with DSC agency", "Aadhar OTP/video verification support", "USB token or cloud DSC setup"],
            excluded: ["DSC renewal (charged separately)", "More than 2 directors in base package", "Hardware token replacement if lost"],
            documents: ["PAN card (Directors)", "Aadhar card (for OTP)", "Passport-size photograph", "Email ID + Mobile number for OTP"],
            riskNote: "Aadhar-mobile linking failure causes delay — verify linkage before starting process"
        },
        {
            id: "03", name: "Name Approval (RUN/SPICe+)", icon: <CheckSquare size={20} className="text-fuchsia-600" />, govt: "₹1,000 (RUN)", prof: "₹1,500-2,500", risk: "MEDIUM", category: "Registration", riskColor: "orange",
            sla: "2-5 business days",
            included: ["Research of 3 proposed company names on MCA", "Availability check + trademark conflict screening", "Submission via RUN or SPICe+ Part A", "Up to 2 resubmissions if name rejected", "Name approval certificate handling"],
            excluded: ["Trademark registration (separate service)", "More than 3 name options in one application", "Legal clearance for brand names"],
            documents: ["Proposed company names (up to 3 options)", "Nature of business (NIC code)", "State of incorporation", "Significance of name if coined word"],
            riskNote: "Common names rejected frequently — always prepare 5 backup names internally before filing"
        },
        {
            id: "04", name: "Incorporation Filing (SPICe+)", icon: <FileSignature size={20} className="text-orange-600" />, govt: "₹0 (up to ₹15L) + Stamp Duty", prof: "₹5,000-12,000", risk: "HIGH", category: "Registration", riskColor: "rose",
            sla: "7-10 working days",
            included: ["SPICe+ integrated form filing (Part A + B)", "MoA & AoA drafting", "AGILE-PRO-S form (GST/PF/ESIC/Bank)", "Certificate of Incorporation (CIN)", "First Board Resolution drafting", "Registered office address establishment", "Share certificate template creation"],
            excluded: ["Stamp duty for states outside Tamil Nadu", "Share capital above ₹10L (additional fees)", "Nominee director service"],
            documents: ["DSC of all proposed directors", "Identity proof (PAN, Aadhar, Passport for NRIs)", "Address proof of directors", "Proof of registered office (rent agreement + NOC)", "Utility bill (not older than 2 months)", "Subscriber Sheet (signed by all)"],
            riskNote: "Address proof mismatch is the #1 cause of rejection — utility bill must exactly match registered address"
        },
        {
            id: "05", name: "PAN & TAN", icon: <CreditCard size={20} className="text-emerald-600" />, govt: "₹110 (PAN) + ₹65 (TAN)", prof: "₹500-1,000", risk: "LOW", category: "Tax & Compliance", riskColor: "emerald",
            sla: "3-7 business days",
            included: ["PAN application for company (Form 49A)", "TAN application (Form 49B)", "Coordination with NSDL/UTI portal", "PAN/TAN certificate follow-up", "Physical PAN card delivery coordination"],
            excluded: ["PAN for individual directors (their own responsibility)", "TDS filing (separate retainer service)"],
            documents: ["Certificate of Incorporation", "Registered office address proof", "Authorized signatory details"],
            riskNote: "PAN delay directly blocks bank account opening and GST registration — prioritize early in parallel"
        },
        {
            id: "06", name: "Bank Account Setup", icon: <Building2 size={20} className="text-blue-600" />, govt: "NIL", prof: "₹1,500-3,000", risk: "MEDIUM", category: "Registration", riskColor: "orange",
            sla: "5-10 working days",
            included: ["Bank identification (ICICI/HDFC/Kotak/SBI/YES Bank)", "Document preparation for KYC", "Relationship manager coordination", "Account opening form assistance", "Net banking + cheque book setup", "Debit card application"],
            excluded: ["Loan or overdraft facility (separate banking service)", "International banking setup", "Minimum balance maintenance"],
            documents: ["CIN Certificate", "PAN of company", "MOA + AOA", "Board Resolution for account opening", "KYC of all directors (PAN + Aadhar + Photo)", "Registered office address proof"],
            riskNote: "Some banks require physical visit — HDFC/ICICI/Kotak have doorstep options in Chennai; recommend accordingly"
        },
        {
            id: "07", name: "GST Registration", icon: <Calculator size={20} className="text-purple-600" />, govt: "NIL", prof: "₹2,500-5,000", risk: "MEDIUM", category: "Tax & Compliance", riskColor: "orange",
            sla: "7-10 working days",
            included: ["GST registration application (GST REG-01)", "ARN tracking and follow-up", "GSTIN certificate download", "HSN/SAC code identification for business", "GST category determination (Regular/Composition)", "First return guidance (GSTR-3B orientation)", "GST invoice template creation"],
            excluded: ["Monthly/Quarterly GST return filing (retainer)", "GST audit or reconciliation", "LUT filing for exporters (add-on)", "Input Tax Credit advisory"],
            documents: ["PAN of company", "Certificate of Incorporation", "Promoter PAN + Aadhar", "Place of business proof (rent agreement + utility bill)", "Bank account (cancelled cheque or statement)", "Digital photo of place of business", "Authorized signatory DSC"],
            riskNote: "TRN-1 rejection due to address mismatch is very common — run a pre-submission document check"
        },
        {
            id: "08", name: "MSME / Udyam Registration", icon: <FileSpreadsheet size={20} className="text-cyan-600" />, govt: "NIL (completely free)", prof: "₹500-1,500", risk: "LOW", category: "Licenses", riskColor: "emerald",
            sla: "Same day to 2 days",
            included: ["Udyam Registration portal filing", "NIC code classification", "Udyam Registration Certificate", "MSME classification guidance (Micro/Small/Medium)", "Benefits briefing (priority lending, collateral-free loans, tenders)"],
            excluded: ["Bank loan facilitation", "Govt scheme applications under MSME", "Udyam Verification for tenders (client responsibility)"],
            documents: ["Aadhar of business owner/director", "PAN of company", "GSTIN (if available)", "Bank account details", "Nature of business + NIC code"],
            riskNote: "Self-certification basis — ensure turnover/investment figures are accurate to avoid future audit issues"
        },
        {
            id: "09", name: "Startup India (DPIIT)", icon: <Rocket size={20} className="text-emerald-500" />, govt: "NIL", prof: "₹2,000-5,000", risk: "LOW", category: "Registration", riskColor: "emerald",
            sla: "2-5 working days",
            included: ["DPIIT recognition application on Startup India portal", "Entity profile creation", "Innovation/scalability statement drafting", "Certificate of Recognition", "80-IAC tax exemption eligibility assessment", "Fund of Funds / angel investor eligibility briefing"],
            excluded: ["80-IAC application to CBDT (separate, requires CA Certificate)", "Pitch deck preparation", "VC/angel investor introductions"],
            documents: ["CIN + Incorporation Certificate", "PAN", "Brief about innovation/scalability of business", "Director details"],
            riskNote: "Only eligible if incorporated within last 10 years and not in prohibited sectors — verify before applying"
        },
        {
            id: "10", name: "EPF & ESIC Registration", icon: <ShieldCheck size={20} className="text-amber-500" />, govt: "NIL", prof: "₹2,000-4,000", risk: "LOW", category: "Tax & Compliance", riskColor: "emerald",
            sla: "5-7 working days",
            included: ["EPF registration on EPFO portal (mandatory 20+ employees)", "ESIC registration (mandatory 10+ employees)", "PF/ESIC code allotment", "Employee enrollment guidance", "Contribution rate briefing (12%+12% PF; 0.75%+3.25% ESIC)", "First challan payment setup"],
            excluded: ["Monthly PF/ESIC challan (retainer service)", "Employee PF account management", "PF withdrawal or transfer assistance"],
            documents: ["CIN + PAN", "Address proof of establishment", "List of employees with salary details", "Bank account details", "DSC of authorized person"],
            riskNote: "Voluntary registration recommended even below threshold — improves credibility with Amazon/Flipkart seller verification"
        },
        {
            id: "11", name: "Professional Tax (Tamil Nadu)", icon: <Briefcase size={20} className="text-rose-600" />, govt: "₹1,000-2,500 (TN fee)", prof: "₹1,000-2,000", risk: "MEDIUM", category: "Tax & Compliance", riskColor: "orange",
            sla: "5-10 working days",
            included: ["PT registration with TN Commercial Taxes Dept", "Employer PT certificate", "Employee PT slab guidance", "First payment guidance", "Certificate display requirement briefing"],
            excluded: ["Monthly PT deduction and remittance (retainer)", "PT variations above 6-month brackets"],
            documents: ["CIN + PAN", "Establishment address proof", "Employee count + salary range", "Director/Employer details"],
            riskNote: "Mandatory for all Chennai-based companies — penalties for non-registration are very common in Tamil Nadu"
        },
        {
            id: "12", name: "Statutory Auditor Appointment", icon: <FileSearch size={20} className="text-blue-500" />, govt: "₹300 (ADT-1 filing)", prof: "₹1,500-3,000", risk: "HIGH", category: "Tax & Compliance", riskColor: "rose",
            sla: "3-5 working days (within 30 days of CIN)",
            included: ["Identification of eligible CA firm for statutory audit", "Consent letter from auditor", "Form ADT-1 filing on MCA portal", "Board Resolution for appointment", "Auditor Certificate of eligibility check"],
            excluded: ["Actual audit conduct", "Audit fee negotiation with auditor", "Tax audit (separate CA engagement)"],
            documents: ["CIN", "Board Resolution (drafted by us)", "Auditor COP + Peer Review certificate", "Consent letter from auditor"],
            riskNote: "Must be done within 30 days of CIN — penalty ₹300/day if delayed. This is most commonly missed."
        },
        {
            id: "13", name: "Shop & Establishment", icon: <Store size={20} className="text-pink-600" />, govt: "₹1,000-5,000 (Based on count)", prof: "₹1,500-3,000", risk: "MEDIUM", category: "Licenses", riskColor: "orange",
            sla: "7-15 working days",
            included: ["Tamil Nadu Shops & Establishments Act registration", "Application to Labour Department", "Certificate of Registration", "Display board requirement briefing", "Annual renewal reminder setup"],
            excluded: ["Renewal filing after first year (add-on service)", "Labour compliance advisory", "Factory Act registration (separate)"],
            documents: ["CIN + PAN", "Business address proof (rent agreement)", "Name and nature of establishment", "Manager/Owner details", "Employee count"],
            riskNote: "Physical inspection may be required in some Chennai zones — prepare premises before applying to avoid delays"
        },
        {
            id: "14", name: "IEC (Import Export Code)", icon: <Plane size={20} className="text-indigo-500" />, govt: "₹500 (DGFT portal fee)", prof: "₹2,000-4,000", risk: "LOW", category: "Licenses", riskColor: "emerald",
            sla: "2-5 working days",
            included: ["IEC application on DGFT portal", "Bank certificate coordination", "IE Code certificate download", "Port code identification", "ICEGATE portal guidance", "Annual IEC updation reminder"],
            excluded: ["Export documentation (Shipping Bill, Bill of Lading)", "Forex management / RBI compliance", "EPCG or MEIS scheme applications"],
            documents: ["PAN of entity", "CIN + Incorporation documents", "Bank certificate on letterhead", "Address proof of entity", "Digital photo + DSC of authorized person"],
            riskNote: "Bank certificate format must exactly match DGFT requirement — use the bank's standard DGFT format letter"
        },
        {
            id: "15", name: "FSSAI License", icon: <HeartHandshake size={20} className="text-fuchsia-500" />, govt: "₹100 (Basic) / ₹2,000-7,500", prof: "₹3,000-8,000", risk: "HIGH", category: "Licenses", riskColor: "rose",
            sla: "30-60 days (State License)",
            included: ["FSSAI category determination (Basic/State/Central)", "Application on FoSCoS portal", "FBO (Food Business Operator) profile setup", "Product category classification", "License tracking and follow-up", "FSSAI compliance requirements briefing", "First renewal reminder"],
            excluded: ["Product testing / lab reports (client responsibility)", "Premise inspection preparation", "FSSAI display board (client to arrange)", "Annual renewal (add-on service)"],
            documents: ["CIN + PAN", "Proof of business address", "List of food products/categories", "Nature of food business (manufacturing/trading)", "Director/Owner photo ID", "Form B declaration"],
            riskNote: "Govt inspection can take 30-60 days — clients must NOT start food business operations before FSSAI is in hand"
        },
        {
            id: "16", name: "Amazon/Flipkart Seller Setup", icon: <ShoppingCart size={20} className="text-orange-500" />, govt: "NIL", prof: "₹5,000-15,000", risk: "MEDIUM", category: "E-Commerce", riskColor: "orange",
            sla: "5-10 working days (standard categories)",
            included: ["Amazon Seller Central account creation", "Seller profile optimization (business name, logo)", "Product listing template (up to 5 SKUs)", "Brand Registry eligibility check", "Flipkart Seller Hub registration", "FBA enrollment and guidance", "Category approval application (restricted categories)", "First ASIN creation walkthrough", "Seller Support contact setup"],
            excluded: ["Ongoing account management (retainer service)", "PPC campaign management", "A+ Content creation", "Return & refund policy management", "Inventory management"],
            documents: ["GSTIN", "Company PAN", "Bank account (cancelled cheque)", "Business address proof", "Product images + descriptions (client to provide)", "Trademark certificate (if Brand Registry)", "Government ID of account holder"],
            riskNote: "Brand registry requires a registered trademark; otherwise, generic listing restrictions apply."
        },
        {
            id: "17", name: "Payment Gateway Integration", icon: <Smartphone size={20} className="text-cyan-500" />, govt: "NIL", prof: "₹3,000-6,000", risk: "MEDIUM", category: "E-Commerce", riskColor: "orange",
            sla: "3-7 working days",
            included: ["Merchant account with Razorpay / Cashfree / PayU", "KYC document submission", "API key generation", "Website integration support (WooCommerce/Shopify plug-and-play)", "Test transaction verification", "Settlement cycle configuration (T+2 or T+7)", "Refund flow testing"],
            excluded: ["Custom payment flow development", "PCI-DSS compliance for high-volume merchants", "International gateway (Stripe/PayPal — separate)", "Subscription billing setup"],
            documents: ["CIN + PAN", "GSTIN", "Bank account (cancelled cheque)", "Company website URL", "Business description", "Director PAN + Aadhar", "Estimated monthly volume"],
            riskNote: "Razorpay may freeze accounts for restricted business categories — verify category before onboarding to avoid freeze"
        },
        {
            id: "18", name: "Website & Domain Setup", icon: <Globe size={20} className="text-blue-400" />, govt: "NIL", prof: "₹8,000-25,000", risk: "LOW", category: "E-Commerce", riskColor: "emerald",
            sla: "10-15 working days post content receipt",
            included: ["Domain registration (.in/.com) for 1 year", "WordPress hosting setup", "5-page static website (Home, About, Products, Contact, Privacy)", "SSL certificate installation", "Google Analytics integration", "Google Search Console setup", "Basic SEO configuration", "Company email IDs (up to 5 IDs)"],
            excluded: ["Custom development or WooCommerce store (add-on)", "Ongoing content updates", "Digital marketing / SEO campaigns", "Social media management"],
            documents: ["Company name and logo (or brief for logo design)", "Brand color preferences", "Content for each page (client provides)", "Domain name preferences (3 options)"],
            riskNote: "Client content delays are the #1 cause of website delays — enforce 5-business-day content submission SLA in contract"
        },
        {
            id: "19", name: "Compliance Calendar Creation", icon: <CalendarCheck size={20} className="text-purple-500" />, govt: "NIL", prof: "₹2,000-5,000 (one-time)", risk: "LOW", category: "Tax & Compliance", riskColor: "emerald",
            sla: "3-5 working days",
            included: ["Customized 12-month compliance calendar (entity-specific)", "GST filing due dates (GSTR-1, 3B, 9, 9C)", "MCA/ROC filing dates (AOC-4, MGT-7, DIR-3 KYC)", "TDS/TCS due dates", "Professional Tax & EPF/ESIC due dates", "FSSAI renewal dates + IEC update deadline", "Board meeting and AGM reminders", "WhatsApp/email reminder system setup"],
            excluded: ["Actual filing of returns (retainer service)", "State-specific local body compliance (if any)"],
            documents: ["CIN + GSTIN", "List of applicable licenses", "Financial year of company", "Any existing compliance history"],
            riskNote: "Missed deadlines result in severe penalties — this service is critical for protecting both client and firm from liability"
        },
        {
            id: "20", name: "Ongoing ROC / GST Retainer", icon: <Repeat size={20} className="text-emerald-400" />, govt: "Late fees if filing delayed (client liability)", prof: "₹3,000-15,000/month", risk: "HIGH", category: "Retainer", riskColor: "rose",
            sla: "Filing before statutory due date",
            included: ["Monthly GST returns (GSTR-1 + GSTR-3B)", "Quarterly TDS returns (24Q/26Q)", "Annual ROC filings (AOC-4 + MGT-7)", "DIR-3 KYC (annual)", "Professional Tax monthly remittance", "EPF/ESIC monthly challan", "Board meeting minutes (quarterly)", "Compliance health report (monthly email)", "WhatsApp/email support (response within 24 hours)"],
            excluded: ["Statutory audit (separate CA engagement)", "Income Tax Return (add-on for ₹5,000-₹15,000)", "Litigation or notices (charged separately)", "International taxation"],
            documents: ["Sales + Purchase invoices (monthly)", "Bank statements (monthly)", "Expense vouchers", "Employee salary statements (for TDS)"],
            riskNote: "Clients submitting documents late is the top operational risk — enforce document submission by the 5th of each month"
        },
    ];

    // Filter logic intersecting BOTH the pricing tier package and the selected category
    const filteredServices = services.filter(s => {
        // 1. Must be included in the selected pricing package
        if (!baseServiceIds.includes(s.id)) return false;

        // 2. Must match the selected category (if not viewing 'All')
        if (activeFilter === 'All') return true;
        return s.category === activeFilter;
    });

    const [expandedId, setExpandedId] = useState(null);

    // Helper functions for Risk Badge styling
    const getRiskBadgeStyles = (color) => {
        switch (color) {
            case 'emerald': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
            case 'orange': return 'bg-amber-50 text-amber-700 border-amber-200';
            case 'rose': return 'bg-rose-50 text-rose-700 border-rose-200';
            default: return 'bg-slate-50 text-slate-700 border-slate-200';
        }
    };

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
                            onClick={() => onNavigate('packages-pricing')}
                            className="flex items-center gap-2 text-slate-500 hover:text-indigo-600 transition-colors font-bold text-sm"
                        >
                            <ArrowLeft size={18} /> Back
                        </button>
                        <div
                            className="cursor-pointer flex items-center gap-2 group"
                            onClick={() => onNavigate('packages-pricing')} // Clicking logo here takes you back to packages
                        >
                            <div className="text-2xl font-black tracking-tighter text-slate-900 group-hover:text-indigo-600 transition-colors">IBZ</div>
                        </div>
                    </div>
                    <div className="flex-1 flex justify-center items-center">
                        {/* Centered area cleared to match Packages pricing page */}
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

                <div className="max-w-[1400px] mx-auto px-6 pt-16">

                    <div className="mb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <h2 className="text-5xl font-black text-slate-900 mb-6 tracking-tight">
                            {pageContent.title} <span className="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-500 to-purple-600 text-5xl">({pageContent.highlight})</span>
                        </h2>
                        <p className="text-slate-500 text-lg font-medium max-w-4xl leading-relaxed">
                            {pageContent.description}
                        </p>
                        <div className="w-full h-px bg-slate-200 mt-10"></div>
                    </div>

                    {/* Filter Chips */}
                    <div className="flex flex-wrap gap-3 mb-10">
                        <button
                            onClick={() => setActiveFilter('All')}
                            className={`px-6 py-2.5 rounded-full text-sm font-bold transition-all duration-300 ${activeFilter === 'All'
                                ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/20 scale-105'
                                : 'bg-white text-slate-600 border border-slate-200 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50/30'
                                }`}
                        >
                            All ({baseServiceIds.length})
                        </button>
                        {categories.map(category => (
                            <button
                                key={category}
                                onClick={() => setActiveFilter(category)}
                                className={`px-6 py-2.5 rounded-full text-sm font-bold transition-all duration-300 ${activeFilter === category
                                    ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/20 scale-105'
                                    : 'bg-white text-slate-600 border border-slate-200 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50/30'
                                    }`}
                            >
                                {category}
                            </button>
                        ))}
                    </div>

                    {/* Services Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                        {filteredServices.map((service, idx) => (
                            <div
                                key={idx}
                                onClick={() => setExpandedId(expandedId === service.id ? null : service.id)}
                                className={`group relative bg-white rounded-[1.5rem] border ${expandedId === service.id ? 'border-indigo-400 shadow-2xl shadow-indigo-500/10' : 'border-slate-100 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-500/5 hover:-translate-y-1'} p-6 flex flex-col items-start gap-5 transition-all duration-300 cursor-pointer overflow-hidden`}
                            >
                                <div className="flex items-start gap-5 w-full">
                                    {/* Identifier Bubble */}
                                    <div className="w-12 h-12 rounded-2xl bg-slate-900 text-white flex items-center justify-center font-black text-lg shrink-0 group-hover:bg-indigo-600 group-hover:scale-110 transition-all rotate-3 group-hover:rotate-0 shadow-md">
                                        {service.id}
                                    </div>

                                    <div className="flex-1 w-full min-w-0">
                                        <h3 className="text-lg font-black text-slate-900 mb-4 flex items-center gap-2 group-hover:text-indigo-700 transition-colors tracking-tight truncate">
                                            {service.icon}
                                            <span className="truncate">{service.name}</span>
                                        </h3>

                                        {/* Info Badges */}
                                        <div className="flex flex-wrap gap-2">
                                            <div className="bg-[#fcfaf5] border border-amber-200 text-amber-700 px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest flex items-center shadow-sm">
                                                <span className="text-amber-500 mr-1.5 font-bold">Govt:</span> {service.govt}
                                            </div>
                                            <div className="bg-cyan-50 border border-cyan-200 text-cyan-800 px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest flex items-center shadow-sm">
                                                <span className="text-cyan-600 mr-1.5 font-bold">Prof:</span> {service.prof}
                                            </div>
                                            <div className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest flex items-center shadow-sm border ${getRiskBadgeStyles(service.riskColor)}`}>
                                                <span className="opacity-70 mr-1.5">Risk:</span> {service.risk}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Expandable Details Section */}
                                {expandedId === service.id && (
                                    <div className="w-full mt-4 pt-4 border-t border-slate-100 animate-fade-in-down text-left">

                                        {/* SLA Banner */}
                                        {service.sla && (
                                            <div className="bg-[#fcfaf5] text-amber-900 text-xs font-bold px-4 py-3 rounded-xl flex items-center mb-6 shadow-sm border border-amber-100">
                                                <CalendarCheck className="w-4 h-4 mr-2 text-amber-500" />
                                                SLA: {service.sla}
                                            </div>
                                        )}

                                        {/* What's Included */}
                                        {service.included && (
                                            <div className="mb-5">
                                                <h5 className="text-[10px] font-black text-slate-400 tracking-[0.2em] uppercase mb-3">What's Included</h5>
                                                <ul className="space-y-2">
                                                    {service.included.map((item, i) => (
                                                        <li key={i} className="flex text-sm text-slate-700 font-medium">
                                                            <CheckSquare className="w-4 h-4 text-emerald-500 mr-2 shrink-0 mt-0.5" />
                                                            <span>{item}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}

                                        {/* What's Excluded */}
                                        {service.excluded && (
                                            <div className="mb-5">
                                                <h5 className="text-[10px] font-black text-slate-400 tracking-[0.2em] uppercase mb-3">What's Excluded</h5>
                                                <ul className="space-y-2">
                                                    {service.excluded.map((item, i) => (
                                                        <li key={i} className="flex text-sm text-slate-500 font-medium">
                                                            <span className="w-4 h-0.5 bg-slate-300 mr-2 shrink-0 mt-2 rounded"></span>
                                                            <span>{item}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}

                                        {/* Documents Required */}
                                        {service.documents && (
                                            <div className="mb-6">
                                                <h5 className="text-[10px] font-black text-slate-400 tracking-[0.2em] uppercase mb-3">Documents Required</h5>
                                                <ul className="space-y-2">
                                                    {service.documents.map((item, i) => (
                                                        <li key={i} className="flex text-sm text-slate-700 font-medium items-start">
                                                            <FileSpreadsheet className="w-4 h-4 text-slate-300 mr-2 shrink-0 mt-0.5" />
                                                            <span>{item}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}

                                        {/* Risk Note Banner */}
                                        {service.riskNote && (
                                            <div className="bg-emerald-50 text-emerald-800 text-xs font-medium px-4 py-3 rounded-xl flex items-start leading-relaxed border border-emerald-100 mb-2">
                                                <span className="text-emerald-600 font-black mr-2 shrink-0 flex items-center mt-0.5">
                                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
                                                </span>
                                                <span>
                                                    <strong className="font-bold text-emerald-900">Risk Note:</strong> {service.riskNote}
                                                </span>
                                            </div>
                                        )}

                                        {/* Action Button for MSME Automation */}
                                        {service.name.includes("MSME") && (
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    window.dispatchEvent(new CustomEvent('open-chat', {
                                                        detail: { prompt: `I want to generate automation for ${service.name}. Please begin.` }
                                                    }));
                                                }}
                                                className="mt-4 w-full bg-gradient-to-r from-fuchsia-600 to-indigo-600 hover:from-fuchsia-700 hover:to-indigo-700 text-white font-bold py-3.5 px-4 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-fuchsia-600/20 active:scale-[0.98]"
                                            >
                                                <Bot size={18} />
                                                Generate Automation
                                            </button>
                                        )}

                                    </div>
                                )}
                            </div>
                        ))}
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

export default AllServicesPage;
