import React, { useState, useMemo } from 'react';
import { X, Calculator, Plus, Check } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const QuoteGeneratorModal = ({ isOpen, onClose }) => {
    const [clientName, setClientName] = useState("");
    const [selectedPackage, setSelectedPackage] = useState("");

    const [addons, setAddons] = useState({
        trademark: false,
        fssai: false,
        iec: false,
        woocommerce: false,
        epf: false,
        itr: false
    });

    const [retainer, setRetainer] = useState("none");

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

        // Retainer is per month, usually we quote 1st month in one-time setup fee or present it separately.
        // Based on the screenshot, it looks like a single "One-Time Professional Fee" total is generated.
        // We will sum the package + addons, and add 1 month of retainer to the setup total.
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

    // Format currency for PDF (Standard jsPDF fonts do not support the ₹ unicode symbol)
    const formatPDFCurrency = (amount) => {
        const formatted = new Intl.NumberFormat('en-IN', {
            maximumFractionDigits: 0
        }).format(amount);
        return `Rs. ${formatted}`;
    };

    const handleGeneratePDF = () => {
        if (!clientName.trim()) {
            alert("Please enter the Client / Business Name before generating the proposal.");
            return;
        }

        if (!selectedPackage || selectedPackage === 'none') {
            alert("Please select a package first.");
            return;
        }

        const doc = new jsPDF();

        // --- Header ---
        doc.setFillColor(31, 41, 55); // slate-800
        doc.rect(0, 0, 210, 40, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(24);
        doc.setFont("helvetica", "bold");
        doc.text("INFINITE BZ", 14, 25);

        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        doc.text("Business Setup & Compliance", 14, 32);

        doc.setFontSize(20);
        doc.text("PROPOSAL", 150, 25);

        // --- Client Info ---
        doc.setTextColor(50, 50, 50);
        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.text("Prepared For:", 14, 55);

        doc.setFont("helvetica", "normal");
        const finalClientName = clientName.trim() || "Valued Client";
        doc.text(finalClientName, 14, 62);

        const date = new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' });
        doc.text(`Date: ${date}`, 140, 55);

        // --- Table Data Prep ---
        const tableData = [];

        // 1. Package
        const pkg = packages.find(p => p.id === selectedPackage);
        if (pkg) {
            tableData.push([{ content: 'Main Package', colSpan: 2, styles: { fontStyle: 'bold', fillColor: [243, 244, 246] } }]);
            tableData.push([pkg.name, formatPDFCurrency(pkg.price)]);
        }

        // 2. Add-ons
        const activeAddons = Object.entries(addons).filter(([k, v]) => v);
        if (activeAddons.length > 0) {
            tableData.push([{ content: 'Add-On Services', colSpan: 2, styles: { fontStyle: 'bold', fillColor: [243, 244, 246] } }]);
            // Map the keys to human readable labels
            const addonLabels = {
                trademark: 'Trademark Registration',
                fssai: 'FSSAI License',
                iec: 'IEC Code',
                woocommerce: 'WooCommerce Store',
                epf: 'EPF/ESIC Registration',
                itr: 'ITR Filing'
            };
            activeAddons.forEach(([key]) => {
                tableData.push([addonLabels[key], formatPDFCurrency(addonPrices[key])]);
            });
        }

        // 3. Retainer
        const ret = retainerPrices.find(r => r.id === retainer);
        if (ret && ret.id !== 'none') {
            tableData.push([{ content: 'Monthly Retainer', colSpan: 2, styles: { fontStyle: 'bold', fillColor: [243, 244, 246] } }]);
            tableData.push([ret.name, formatPDFCurrency(ret.price)]);
        }

        // --- Generate Table ---
        autoTable(doc, {
            startY: 75,
            head: [['Description', 'Amount']],
            body: tableData,
            theme: 'striped',
            headStyles: { fillColor: [79, 70, 229] }, // Indigo-600
            columnStyles: {
                0: { cellWidth: 130 },
                1: { cellWidth: 40, halign: 'right' }
            },
            styles: { fontSize: 10, cellPadding: 6 }
        });

        // --- Totals Section ---
        let finalY = doc.lastAutoTable.finalY + 10;

        doc.setFontSize(10);
        doc.setTextColor(80, 80, 80);
        doc.text("Professional Subtotal:", 130, finalY);
        doc.text(formatPDFCurrency(calculation.subtotal), 184, finalY, { align: 'right' });

        doc.text("GST (18%):", 130, finalY + 8);
        doc.text(formatPDFCurrency(calculation.gst), 184, finalY + 8, { align: 'right' });

        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(17, 24, 39); // Gray-900
        doc.text("Grand Total:", 130, finalY + 18);
        doc.text(formatPDFCurrency(calculation.grandTotal), 184, finalY + 18, { align: 'right' });

        // --- Footer Note ---
        doc.setFont("helvetica", "italic");
        doc.setFontSize(9);
        doc.setTextColor(100, 100, 100);
        const footerY = finalY + 40;
        doc.text("* Note: Above quote is for professional fees only. Government fees, stamp duty, ", 14, footerY);
        doc.text("and out-of-pocket expenses are not included and will be charged at actuals.", 14, footerY + 5);

        // --- Save PDF ---
        const fileName = `${finalClientName.replace(/\s+/g, '_')}_IBZ_Proposal.pdf`;
        doc.save(fileName);

        // --- Store in LocalStorage ---
        try {
            const pdfBase64 = doc.output('datauristring');
            const savedProposals = JSON.parse(localStorage.getItem('ibz_proposals') || '[]');

            savedProposals.push({
                id: Date.now().toString(),
                clientName: finalClientName,
                date: date,
                amount: calculation.grandTotal,
                fileName: fileName,
                pdfData: pdfBase64
            });

            localStorage.setItem('ibz_proposals', JSON.stringify(savedProposals));
        } catch (error) {
            console.error("Could not save to localStorage (might be too large)", error);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
                className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"
                onClick={onClose}
            ></div>

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
                        <p className="text-sm font-medium text-slate-500 mt-1 ml-11">Build a custom proposal for your client</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="flex items-center gap-2 px-4 py-2 hover:bg-slate-100 text-slate-500 rounded-xl transition-colors font-bold text-sm"
                    >
                        <X size={16} /> Close
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="overflow-y-auto px-8 py-6 flex-1 space-y-8">

                    {/* Client Name */}
                    <div>
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
                        className="w-full py-4 bg-gradient-to-r from-indigo-600 to-fuchsia-600 hover:from-indigo-700 hover:to-fuchsia-700 text-white rounded-xl font-black shadow-lg shadow-indigo-600/20 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2"
                    >
                        <Calculator size={18} />
                        Generate Proposal PDF
                    </button>
                </div>

            </div>
        </div>
    );
};

export default QuoteGeneratorModal;
