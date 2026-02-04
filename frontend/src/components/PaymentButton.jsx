import React from 'react';

const PaymentButton = ({ amount, userDetails, onPaymentSuccess, eventId }) => {

    const handlePayment = async () => {
        try {
            const token = localStorage.getItem('token');
            // 1. Ask Backend to Create an Order
            const res = await fetch('/api/v1/payment/create-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ amount: amount, currency: "INR" })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to create order");
            }

            const data = await res.json();

            // 2. Setup Razorpay Options
            const options = {
                key: data.key_id,
                amount: data.amount,
                currency: data.currency,
                name: "Infinite BZ",
                description: "Event Ticket Registration",
                order_id: data.id, // The Order ID from Backend

                handler: async function (response) {
                    // 3. Payment Success - Now Verify with Backend
                    const verifyPayload = {
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_signature: response.razorpay_signature
                    };

                    try {
                        const verifyRes = await fetch('/api/v1/payment/verify', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`
                            },
                            body: JSON.stringify(verifyPayload)
                        });

                        if (!verifyRes.ok) throw new Error("Verification failed");

                        const verifyData = await verifyRes.json();

                        if (verifyData.status === "success") {
                            // Notify parent component that payment succeeded
                            onPaymentSuccess(response.razorpay_payment_id);
                        }
                    } catch (error) {
                        console.error("Verification error:", error);
                        alert("Payment Verification Failed! Do not issue ticket.");
                    }
                },
                prefill: {
                    name: userDetails?.full_name || "",
                    email: userDetails?.email || "",
                    contact: userDetails?.phone || ""
                },
                theme: {
                    color: "#3399cc"
                }
            };

            // Open Razorpay Popup
            const rzp1 = new window.Razorpay(options);
            rzp1.open();

        } catch (error) {
            console.error("Error in payment flow:", error);
            alert("Payment failed initialization: " + error.message);
        }
    };

    return (
        <button onClick={handlePayment} className="bg-sky-500 hover:bg-sky-600 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg shadow-sky-500/20">
            Pay ₹{amount} & Register
        </button>
    );
};

export default PaymentButton;
