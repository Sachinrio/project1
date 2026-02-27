import { useState } from 'react';
import { createPortal } from 'react-dom';
import { X, CheckCircle2, CreditCard, ChevronRight } from 'lucide-react';

export default function ServiceCheckoutModal({ isOpen, onClose, serviceName, price, user }) {
    if (!isOpen || !serviceName) return null;

    const [isProcessing, setIsProcessing] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    const handleConfirm = async () => {
        setIsProcessing(true);

        // Bypass payment process entirely
        setTimeout(() => {
            setIsProcessing(false);
            setIsSuccess(true);

            if (serviceName.toLowerCase().includes('msme')) {
                // Instantly open the global chatbot and inject the context
                window.dispatchEvent(new CustomEvent('open-chat', {
                    detail: { prompt: `I have successfully registered for ${serviceName}. Please begin the MSME automation script.` }
                }));
            }
        }, 800);
    };

    const verifyAndComplete = async (paymentDetails) => {
        try {
            const token = localStorage.getItem('token');
            const verifyRes = await fetch('/api/v1/payment/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token && { 'Authorization': `Bearer ${token}` })
                },
                body: JSON.stringify({
                    razorpay_order_id: paymentDetails.razorpay_order_id,
                    razorpay_payment_id: paymentDetails.razorpay_payment_id,
                    razorpay_signature: paymentDetails.razorpay_signature
                })
            });

            if (!verifyRes.ok) throw new Error("Verification failed");
            const verifyData = await verifyRes.json();

            if (verifyData.status === "success") {
                setIsProcessing(false);
                setIsSuccess(true);
            }

        } catch (error) {
            console.error(error);
            alert("Payment verification failed!");
            setIsProcessing(false);
        }
    };

    if (isSuccess) {
        return createPortal(
            <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
                <div className="bg-slate-900 w-full max-w-md rounded-2xl border border-slate-800 shadow-2xl p-8 text-center">
                    <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                        <CheckCircle2 size={32} className="text-emerald-500" />
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-2">Payment Successful!</h2>
                    <p className="text-slate-400 mb-8">
                        You have successfully registered for:<br />
                        <span className="text-white font-bold block mt-2">{serviceName}</span>
                    </p>
                    <button
                        onClick={onClose}
                        className="w-full bg-slate-800 hover:bg-slate-700 text-white py-3 rounded-xl font-bold transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>,
            document.body
        );
    }

    const modalContent = (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
            <div className="bg-slate-900 w-full max-w-xl rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-950">
                    <div>
                        <h2 className="text-xl font-bold text-white">Startup Service Checkout</h2>
                        <p className="text-fuchsia-400 text-sm font-medium">{serviceName}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-6">
                    {/* Order Summary */}
                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50 space-y-4">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <CheckCircle2 className="text-fuchsia-500" /> Order Summary
                        </h3>
                        <div className="flex justify-between text-sm border-b border-slate-700/50 pb-4">
                            <span className="text-slate-300 font-medium">{serviceName}</span>
                            <span className="font-bold text-white">₹{price}</span>
                        </div>
                        <div className="flex justify-between items-end">
                            <span className="text-slate-400 font-bold uppercase tracking-wide">Total Payble</span>
                            <span className="text-3xl font-black text-white">₹{price}</span>
                        </div>
                    </div>

                    <div className="bg-slate-900 border border-slate-700 p-4 rounded-xl flex items-start gap-3">
                        <div className="p-2 bg-slate-800 rounded-lg text-fuchsia-500">
                            <CreditCard size={20} />
                        </div>
                        <div>
                            <h4 className="font-bold text-white text-sm">Secure Payment</h4>
                            <p className="text-xs text-slate-500 mt-1">
                                Payments are processed securely via Razorpay.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-800 bg-slate-950 flex justify-end">
                    <button
                        onClick={handleConfirm}
                        disabled={isProcessing}
                        className="bg-fuchsia-600 hover:bg-fuchsia-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg shadow-fuchsia-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {isProcessing ? 'Processing...' : 'Simulate Payment'}
                        {!isProcessing && <ChevronRight size={18} />}
                    </button>
                </div>
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
}
