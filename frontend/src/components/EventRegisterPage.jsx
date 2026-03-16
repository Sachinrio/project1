import React, { useState, useEffect } from 'react';
import PaymentButton from './PaymentButton';
import { ArrowLeft } from 'lucide-react';

const EventRegisterPage = ({ onNavigate }) => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        // Fetch user details for prefilling payment form
        const fetchUser = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const res = await fetch('/api/v1/user/profile', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (res.ok) {
                        const data = await res.json();
                        setUser(data);
                    }
                } catch (e) {
                    console.error("Failed to load user profile", e);
                }
            }
        };
        fetchUser();
    }, []);

    const handleSuccess = (paymentId) => {
        alert("Success! Ticket Booked with Payment ID: " + paymentId);
        // Redirect to a "Registration Success" or "My Tickets" page here
        onNavigate('my-registrations');
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white p-6">
            <div className="max-w-2xl mx-auto">
                <button onClick={() => onNavigate('dashboard')} className="flex items-center gap-2 text-slate-400 hover:text-white mb-8">
                    <ArrowLeft size={20} /> Back to Dashboard
                </button>

                <div className="bg-slate-800 rounded-2xl p-8 border border-white/5">
                    <h1 className="text-3xl font-bold mb-4">Smart AI Development Conference</h1>
                    <p className="text-slate-400 mb-8">Join us for an immersive deep dive into the future of AI technology.</p>

                    <div className="flex items-center justify-between bg-slate-900 p-6 rounded-xl border border-white/5 mb-8">
                        <div>
                            <div className="text-sm text-slate-500 uppercase font-bold tracking-wider mb-1">Total Amount</div>
                            <div className="text-3xl font-bold text-white">₹1.00 <span className="text-sm font-normal text-slate-500">(Testing)</span></div>
                        </div>
                        <div className="text-right">
                            <div className="text-sm text-slate-500 mb-1">Date</div>
                            <div className="font-semibold">Oct 24, 2024</div>
                        </div>
                    </div>

                    <div className="text-center">
                        {/* 1 Rupee Test Payment Button */}
                        <PaymentButton
                            amount={1}
                            userDetails={user}
                            onPaymentSuccess={handleSuccess}
                        />
                        <p className="mt-4 text-xs text-slate-500">Secured by Razorpay</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EventRegisterPage;
