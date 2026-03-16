import { useState } from 'react';
import { X, Building2, Smartphone, User, CreditCard, ShieldCheck } from 'lucide-react';

export default function BankDetailsModal({ isOpen, onClose, onSuccess, user }) {
    if (!isOpen) return null;

    const [form, setForm] = useState({
        account_holder_name: user?.full_name || "",
        account_number: "",
        confirm_account_number: "",
        ifsc_code: "",
        mobile_number: user?.phone || ""
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        // Validation
        if (form.account_number !== form.confirm_account_number) {
            setError("Account numbers do not match.");
            return;
        }
        if (form.ifsc_code.length !== 11) {
            setError("Invalid IFSC Code format (Must be 11 characters)");
            return;
        }
        if (!form.account_number || !form.ifsc_code || !form.account_holder_name) {
            setError("Please fill all mandatory fields.");
            return;
        }

        setLoading(true);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/v1/payment/onboard-organizer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    account_holder_name: form.account_holder_name,
                    account_number: form.account_number,
                    ifsc_code: form.ifsc_code.toUpperCase(),
                    mobile_number: form.mobile_number
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Failed to save bank details");
            }

            const data = await response.json();
            onSuccess(data.razorpay_account_id);

        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-slate-900 w-full max-w-md rounded-2xl border border-slate-800 shadow-2xl relative overflow-hidden">

                {/* Header */}
                <div className="p-6 border-b border-slate-800 bg-slate-950/50">
                    <div className="flex justify-between items-start">
                        <div>
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <Building2 className="text-emerald-500" size={24} /> Payout Details
                            </h2>
                            <p className="text-slate-400 text-sm mt-1">To receive money from paid events.</p>
                        </div>
                        <button onClick={onClose} className="text-slate-500 hover:text-white"><X size={20} /></button>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg text-sm">
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-400 uppercase">Account Holder Name</label>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                            <input
                                name="account_holder_name"
                                value={form.account_holder_name}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-white focus:border-emerald-500 outline-none"
                                placeholder="As per bank records"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-400 uppercase">Bank Account Number</label>
                        <div className="relative">
                            <CreditCard className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                            <input
                                name="account_number"
                                type="password"
                                value={form.account_number}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-white focus:border-emerald-500 outline-none"
                                placeholder="Enter Account Number"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-400 uppercase">Confirm Account Number</label>
                        <div className="relative">
                            <ShieldCheck className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                            <input
                                name="confirm_account_number"
                                type="text"
                                value={form.confirm_account_number}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-white focus:border-emerald-500 outline-none"
                                placeholder="Re-enter Account Number"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-400 uppercase">IFSC Code</label>
                            <input
                                name="ifsc_code"
                                value={form.ifsc_code}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-emerald-500 outline-none uppercase"
                                placeholder="HDFC000..."
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-400 uppercase">Mobile</label>
                            <div className="relative">
                                <Smartphone className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                                <input
                                    name="mobile_number"
                                    value={form.mobile_number}
                                    onChange={handleChange}
                                    className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-white focus:border-emerald-500 outline-none"
                                    placeholder="9876543210"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {loading ? "Verifying..." : "Verify & Save Details"}
                        </button>
                    </div>

                </form>
            </div>
        </div>
    );
}
