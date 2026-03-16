import React, { useState, useMemo, useRef } from 'react';
import { X, Calculator, Check, Download } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const QuoteGeneratorModal = ({ isOpen, onClose }) => {
    const [clientName, setClientName] = useState("");
    const [contactPerson, setContactPerson] = useState("");
    const [email, setEmail] = useState("");
    const [contactNumber, setContactNumber] = useState("");
    const [selectedPackage, setSelectedPackage] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");

    const [addons, setAddons] = useState({
        trademark: false,
        fssai: false,
        iec: false,
        woocommerce: false,
        epf: false,
        itr: false
    });

    const [retainer, setRetainer] = useState("none");

    const pdfRef = useRef(null);

    // Pricing Data
    const packages = [
        { id: "none", name: "— Choose a package —", price: 0 },
        { id: "basic", name: "Starter / Basic (₹15,000)", price: 15000 },
        { id: "growth", name: "Growth (₹28,000)", price: 28000 },
        { id: "ecom", name: "E-Com Pro (₹55,000)", price: 55000 },
        { id: "complete", name: "Complete Launch (₹95,000)", price: 95000 }
    ];

    const addonPrices = {
        trademark: 10000,
        fssai: 7000,
        iec: 3000,
        woocommerce: 30000,
        epf: 8000,
        itr: 5000
    };

    const retainerPrices = [
        { id: "none", name: "No retainer", price: 0 },
        { id: "gst_basic", name: "Basic GST & ROC (₹5,000/mo)", price: 5000 },
        { id: "gst_pro", name: "Pro Compliance (₹10,000/mo)", price: 10000 },
        { id: "full", name: "Full Outsourced CFO (₹25,000/mo)", price: 25000 }
    ];

    const handleAddonToggle = (key) => {
        setAddons(prev => ({ ...prev, [key]: !prev[key] }));
    };

    // Calculate Totals
    const calculation = useMemo(() => {
        const pkgPrice = packages.find(p => p.id === selectedPackage)?.price || 0;

        const addonsPrice = Object.entries(addons).reduce((sum, [key, isSelected]) => {
            return isSelected ? sum + addonPrices[key] : sum;
        }, 0);

        const retainerPrice = retainerPrices.find(r => r.id === retainer)?.price || 0;

        const subtotal = pkgPrice + addonsPrice + retainerPrice;
        const gst = subtotal * 0.18;
        const grandTotal = subtotal + gst;

        return { subtotal, gst, grandTotal };
    }, [selectedPackage, addons, retainer]);

    // Format currency
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    };

    // Format currency for PDF
    const formatPDFCurrency = (amount) => {
        const formatted = new Intl.NumberFormat('en-IN', {
            maximumFractionDigits: 0
        }).format(amount);
        return `Rs. ${formatted}`;
    };

    const handleGeneratePDF = async () => {
        if (!clientName.trim() || !contactPerson.trim() || !email.trim() || !contactNumber.trim()) {
            alert("Please fill in all the contact details (Business Name, Contact Person, Email, Contact Number) before generating the proposal.");
            return;
        }

        if (!selectedPackage || selectedPackage === 'none') {
            alert("Please select a package first.");
            return;
        }

        setIsGenerating(true);

        try {
            const element = pdfRef.current;
            element.style.display = 'block'; // Make it visible for canvas capturing

            const canvas = await html2canvas(element, {
                scale: 2,
                useCORS: true,
                logging: false,
                backgroundColor: '#ffffff'
            });

            element.style.display = 'none'; // Hide it again

            const imgData = canvas.toDataURL('image/jpeg', 1.0);

            // A4 sizing
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

            // We'll clip the height if it exceeds a single page, or just let it scale.
            // The template is designed to fit on one A4 page nicely.
            pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, Math.min(pdfHeight, pdf.internal.pageSize.getHeight()));

            // --- Prepare Payload for Backend ---
            const pdfBase64 = pdf.output('datauristring');
            const finalClientName = clientName.trim() || "Valued Client";

            const payload = {
                company_name: finalClientName,
                contact_person: contactPerson,
                email: email,
                contact_number: contactNumber,
                pdf_base64: pdfBase64
            };

            // --- Send Request ---
            const response = await fetch('/api/v1/proposal/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Failed to send proposal email. Check console for details. (Status: ${response.status})`);
            }

            // Show Success
            setSuccessMessage("Proposal generated successfully! The PDF has been sent to the provided email address.");

        } catch (error) {
            console.error("Error generating proposal:", error);
            alert(error.message || "Something went wrong generating the proposal.");
            if (pdfRef.current) pdfRef.current.style.display = 'none';
        } finally {
            setIsGenerating(false);
        }
    };


    // --- Hidden PDF Layout Preparation Data ---
    const finalClientName = clientName.trim() || "Infosys";
    const finalContactPerson = contactPerson.trim() || "Jarvis";
    const dateStr = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    const pkg = packages.find(p => p.id === selectedPackage);
    const activeAddons = Object.entries(addons).filter(([k, v]) => v);
    const addonLabels = {
        trademark: 'Trademark Registration',
        fssai: 'FSSAI License',
        iec: 'IEC Code',
        woocommerce: 'WooCommerce Store',
        epf: 'EPF/ESIC Registration',
        itr: 'ITR Filing'
    };
    const ret = retainerPrices.find(r => r.id === retainer);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
                className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"
                onClick={onClose}
            ></div>

            {/* ---> HIDDEN TEMPLATE FOR HTML2CANVAS <--- */}
            {/* The layout strictly matches the provided user screenshot */}
            <div
                ref={pdfRef}
                className="absolute pointer-events-none"
                style={{
                    display: 'none',
                    width: '794px', // Standard pixel width for A4 at 96 DPI
                    top: '-9999px',
                    left: '-9999px',
                    fontFamily: "'Inter', sans-serif"
                }}
            >
                {/* Outermost wrapper matching screenshot's dark blue background */}
                <div className="w-full min-h-[1100px] flex flex-col bg-[#111827]">

                    {/* Header Dark Blue */}
                    <div className="pt-12 pb-20 px-12 flex justify-between items-start">
                        <div>
                            <h1 className="text-white text-5xl font-black tracking-tight mb-2">INFINITE BZ</h1>
                            <p className="text-[#94a3b8] text-lg leading-snug">Business Setup & Premium<br />Compliance</p>
                        </div>
                        <div>
                            <h2 className="text-[#c084fc] tracking-[0.25em] font-bold text-lg uppercase pt-3">Proposal</h2>
                        </div>
                    </div>

                    {/* Main White Content Card overlapping header */}
                    <div className="px-10 -mt-12 mx-auto relative z-10 w-full mb-12">
                        <div className="bg-white rounded-t-[20px] shadow-sm overflow-hidden min-h-[850px] flex flex-col">

                            {/* Card Header (Client Info) */}
                            <div className="px-12 py-10 pb-12 flex justify-between items-start">
                                <div>
                                    <h3 className="text-[#94a3b8] text-[12px] font-bold tracking-[0.1em] mb-2 uppercase">Prepared For</h3>
                                    <h2 className="text-[#0f172a] text-3xl font-black mb-1">{finalClientName}</h2>
                                    {contactPerson && <p className="text-[#64748b] text-[17px]">Attn: {finalContactPerson}</p>}
                                </div>
                                <div className="text-right">
                                    <h3 className="text-[#94a3b8] text-[12px] font-bold tracking-[0.1em] mb-2 uppercase">Date</h3>
                                    <p className="text-[#0f172a] text-[16px] font-bold">{dateStr}</p>
                                </div>
                            </div>

                            {/* Table Header (Purple Strip) */}
                            <div className="bg-[#6366f1] text-white px-12 py-4 flex justify-between text-[13px] font-bold tracking-[0.05em] uppercase">
                                <span>Description</span>
                                <span>Amount</span>
                            </div>

                            {/* Table Content Area */}
                            <div className="flex-1 space-y-0">

                                {/* Package */}
                                {pkg && pkg.id !== 'none' && (
                                    <>
                                        <div className="px-12 py-5 border-b border-gray-100/50 bg-[#f8fafc]/50">
                                            <h4 className="text-[#64748b] text-[12px] font-bold tracking-[0.1em] uppercase">Main Package</h4>
                                        </div>
                                        <div className="px-12 py-6 flex justify-between items-center group text-[17px]">
                                            <span className="text-[#334155] font-medium">{pkg.name}</span>
                                            <span className="text-[#0f172a] font-bold">{formatPDFCurrency(pkg.price)}</span>
                                        </div>
                                    </>
                                )}

                                {/* Addons */}
                                {activeAddons.length > 0 && (
                                    <>
                                        <div className="px-12 py-5 border-y border-gray-100/50 bg-[#f8fafc]/50">
                                            <h4 className="text-[#64748b] text-[12px] font-bold tracking-[0.1em] uppercase">Add-On Services</h4>
                                        </div>
                                        <div className="px-12 pt-6 pb-4 space-y-8 text-[17px]">
                                            {activeAddons.map(([key]) => (
                                                <div key={key} className="flex justify-between items-center">
                                                    <span className="text-[#334155] font-medium">{addonLabels[key]}</span>
                                                    <span className="text-[#0f172a] font-bold">{formatPDFCurrency(addonPrices[key])}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </>
                                )}

                                {/* Retainer */}
                                {ret && ret.id !== 'none' && (
                                    <>
                                        <div className="px-12 py-5 border-y border-gray-100/50 bg-[#f8fafc]/50 mt-4">
                                            <h4 className="text-[#64748b] text-[12px] font-bold tracking-[0.1em] uppercase">Monthly Retainer</h4>
                                        </div>
                                        <div className="px-12 py-7 flex justify-between items-center text-[17px]">
                                            <span className="text-[#334155] font-medium">{ret.name}</span>
                                            <span className="text-[#0f172a] font-bold">{formatPDFCurrency(ret.price)}</span>
                                        </div>
                                    </>
                                )}
                            </div>

                            {/* Spacer to push totals to bottom if list is short */}
                            <div className="flex-1 min-h-[100px]"></div>

                            {/* Totals Section */}
                            <div className="px-12 mt-auto pt-6 pb-6">
                                <div className="flex justify-end mb-8">
                                    <div className="w-[60%]">
                                        <div className="flex justify-end items-center gap-4 py-2 text-[15px]">
                                            <span className="text-[#64748b] font-medium">Professional Subtotal:</span>
                                            <span className="text-[#0f172a] font-bold w-28 text-right">{formatPDFCurrency(calculation.subtotal)}</span>
                                        </div>
                                        <div className="flex justify-end items-center gap-4 py-2 text-[15px] border-b border-gray-200 pb-5">
                                            <span className="text-[#64748b] font-medium">GST (18%):</span>
                                            <span className="text-[#0f172a] font-bold w-28 text-right">{formatPDFCurrency(calculation.gst)}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Grand Total Box matching screenshot precisely */}
                                <div className="bg-[#f8fafc] rounded-2xl px-10 py-8 flex justify-between items-center">
                                    <span className="text-[#0f172a] text-[20px] font-black tracking-tight">GRAND TOTAL:</span>
                                    <div className="text-right">
                                        <span className="text-[#6366f1] text-[34px] font-bold block mb-1 tracking-tight">{formatPDFCurrency(calculation.grandTotal)}</span>
                                        <span className="text-[#6366f1] text-[11px] font-medium opacity-80 pl-2">www.infinitebz.com</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Grey background that continues below the white card */}
                        <div className="h-64 bg-[#f8fafc] -mx-4 w-[calc(100%+2rem)] absolute bottom-[-16rem] z-[-1] border-t border-gray-200"></div>
                    </div>
                </div>
            </div>
            {/* ---> END HIDDEN TEMPLATE FOR HTML2CANVAS <--- */}


            {/* /// ACTIVE MODAL UI /// */}
            <div className="relative bg-[#fdfdff] w-full max-w-2xl rounded-[2rem] shadow-2xl flex flex-col max-h-[90vh] overflow-hidden border border-slate-200/60 animate-in fade-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-white sticky top-0 z-10">
                    <div>
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600">
                                <Calculator size={18} strokeWidth={2.5} />
                            </div>
                            <h2 className="text-2xl font-black text-slate-900 tracking-tight">Quote Generator</h2>
                        </div>
                        <p className="text-sm font-medium text-slate-500 mt-1 ml-11">Build and email a custom proposal for your client</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="flex items-center gap-2 px-4 py-2 hover:bg-slate-100 text-slate-500 rounded-xl transition-colors font-bold text-sm"
                    >
                        <X size={16} /> Close
                    </button>
                </div>

                {successMessage ? (
                    <div className="flex flex-col items-center justify-center p-12 space-y-4">
                        <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                            <Check size={32} strokeWidth={3} />
                        </div>
                        <h3 className="text-2xl font-bold text-slate-800 text-center">Success!</h3>
                        <p className="text-slate-600 text-center max-w-sm">{successMessage}</p>
                        <button
                            onClick={onClose}
                            className="mt-6 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg transition-colors"
                        >
                            Done
                        </button>
                    </div>
                ) : (
                    <>
                        {/* Scrollable Content */}
                        <div className="overflow-y-auto px-8 py-6 flex-1 space-y-8">

                            {/* Client Name & Contact Info Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="md:col-span-2">
                                    <label className="block text-xs font-black tracking-[0.1em] text-slate-500 uppercase mb-2">
                                        Client / Business Name
                                    </label>
                                    <input
                                        type="text"
                                        placeholder="e.g., FreshBite Foods Pvt Ltd"
                                        value={clientName}
                                        onChange={(e) => setClientName(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all font-medium"
                                    />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="block text-xs font-black tracking-[0.1em] text-slate-500 uppercase mb-2">
                                        Contact Person Name
                                    </label>
                                    <input
                                        type="text"
                                        placeholder="e.g., John Doe"
                                        value={contactPerson}
                                        onChange={(e) => setContactPerson(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all font-medium"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-black tracking-[0.1em] text-slate-500 uppercase mb-2">
                                        Email ID
                                    </label>
                                    <input
                                        type="email"
                                        placeholder="client@example.com"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all font-medium"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-black tracking-[0.1em] text-slate-500 uppercase mb-2">
                                        Contact Number
                                    </label>
                                    <input
                                        type="tel"
                                        placeholder="+91 9876543210"
                                        value={contactNumber}
                                        onChange={(e) => setContactNumber(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all font-medium"
                                    />
                                </div>
                            </div>

                            {/* Select Package */}
                            <div>
                                <label className="block text-xs font-black tracking-[0.1em] text-slate-500 uppercase mb-2">
                                    Select Package
                                </label>
                                <select
                                    value={selectedPackage}
                                    onChange={(e) => setSelectedPackage(e.target.value)}
                                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none cursor-pointer"
                                >
                                    {packages.map(pkg => (
                                        <option key={pkg.id} value={pkg.id}>{pkg.name}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Add-on Services Grid */}
                            <div>
                                <label className="block text-xs font-black tracking-[0.1em] text-slate-500 uppercase mb-3">
                                    Add-On Services
                                </label>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {[
                                        { id: 'trademark', label: `Trademark Reg (${formatCurrency(addonPrices.trademark)})` },
                                        { id: 'fssai', label: `FSSAI License (${formatCurrency(addonPrices.fssai)})` },
                                        { id: 'iec', label: `IEC Code (${formatCurrency(addonPrices.iec)})` },
                                        { id: 'woocommerce', label: `WooCommerce Store (${formatCurrency(addonPrices.woocommerce)})` },
                                        { id: 'epf', label: `EPF/ESIC Reg (${formatCurrency(addonPrices.epf)})` },
                                        { id: 'itr', label: `ITR Filing (${formatCurrency(addonPrices.itr)})` }
                                    ].map((addon) => (
                                        <div
                                            key={addon.id}
                                            onClick={() => handleAddonToggle(addon.id)}
                                            className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all ${addons[addon.id]
                                                ? 'border-indigo-500 bg-indigo-50/50 text-indigo-900'
                                                : 'border-slate-100 bg-slate-50 hover:bg-slate-100 text-slate-600'
                                                }`}
                                        >
                                            <div className={`w-5 h-5 rounded flex items-center justify-center border transition-colors ${addons[addon.id] ? 'bg-indigo-600 border-indigo-600' : 'bg-white border-slate-300'
                                                }`}>
                                                {addons[addon.id] && <Check size={14} className="text-white" strokeWidth={3} />}
                                            </div>
                                            <span className="font-bold text-sm tracking-tight">{addon.label}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Monthly Retainer */}
                            <div>
                                <label className="block text-xs font-black tracking-[0.1em] text-slate-500 uppercase mb-2">
                                    Monthly Retainer
                                </label>
                                <select
                                    value={retainer}
                                    onChange={(e) => setRetainer(e.target.value)}
                                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none cursor-pointer"
                                >
                                    {retainerPrices.map(ret => (
                                        <option key={ret.id} value={ret.id}>{ret.name}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Total Calculator Card */}
                            <div className="bg-slate-900 rounded-[1.5rem] p-8 text-center shadow-2xl shadow-indigo-500/10 relative overflow-hidden group">
                                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-cyan-500"></div>

                                <p className="text-[10px] font-black tracking-[0.2em] text-slate-400 uppercase mb-4">
                                    One-Time Professional Fee
                                </p>

                                <div className="flex items-center justify-center gap-1 mb-2">
                                    <span className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 to-indigo-400 tracking-tighter">
                                        {formatCurrency(calculation.subtotal).replace('₹', '')}
                                    </span>
                                    <span className="text-4xl font-bold text-fuchsia-400">₹</span>
                                </div>

                                <p className="text-slate-400 font-medium text-sm mb-4">
                                    + {formatCurrency(calculation.gst)} GST (18%)
                                </p>

                                <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg backdrop-blur-sm border border-white/5">
                                    <span className="text-white font-bold text-sm">
                                        Grand Total: {formatCurrency(calculation.grandTotal)} + actuals for govt fees
                                    </span>
                                </div>
                            </div>

                        </div>

                        {/* Footer Action */}
                        <div className="p-6 border-t border-slate-100 bg-white">
                            <button
                                onClick={handleGeneratePDF}
                                disabled={isGenerating}
                                className="w-full py-4 bg-gradient-to-r from-indigo-600 to-fuchsia-600 hover:from-indigo-700 hover:to-fuchsia-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-black shadow-lg shadow-indigo-600/20 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2 mb-2"
                            >
                                {isGenerating ? (
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                ) : (
                                    <Calculator size={18} />
                                )}
                                {isGenerating ? "Generating Proposal..." : "Generate Proposal & Send Email"}
                            </button>
                        </div>
                    </>
                )}

            </div>
        </div>
    );
};

export default QuoteGeneratorModal;
