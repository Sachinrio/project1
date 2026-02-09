import { useState } from 'react';
import { ScanLine, CheckCircle2, User, XCircle, Clock } from 'lucide-react';
import Sidebar from './Sidebar';

export default function OrganizerCheckIn({ user, onLogout, onNavigate }) {
    const [ticketId, setTicketId] = useState("");
    const [status, setStatus] = useState("IDLE"); // IDLE, LOADING, SUCCESS, ERROR
    const [result, setResult] = useState(null);
    const [errorMsg, setErrorMsg] = useState("");
    const [recentScans, setRecentScans] = useState([]);

    const handleCheckIn = async (e) => {
        e.preventDefault();
        if (!ticketId.trim()) return;

        setStatus("LOADING");
        setResult(null);
        setErrorMsg("");

        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/events/check-in', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ ticket_id: ticketId.trim() })
            });

            const data = await res.json();

            if (res.ok) {
                setStatus("SUCCESS");
                setResult(data);

                // Add to recent list
                setRecentScans(prev => [
                    {
                        id: data.ticket_id,
                        name: data.attendee,
                        event: data.event,
                        time: new Date().toLocaleTimeString()
                    },
                    ...prev.slice(0, 4) // Keep last 5
                ]);

                setTicketId(""); // Clear input on success
            } else {
                setStatus("ERROR");
                setErrorMsg(data.detail || "Check-in failed");
            }

        } catch (err) {
            console.error("Check-in error:", err);
            setStatus("ERROR");
            setErrorMsg("Network error. Please try again.");
        }
    };

    return (
        <div className="flex min-h-screen bg-slate-950">
            <Sidebar activePage="check-in" onNavigate={onNavigate} onLogout={onLogout} />

            <main className="flex-1 lg:ml-64 p-8 relative overflow-hidden">
                {/* Background Glow */}
                <div className="absolute top-0 left-0 w-full h-96 bg-primary-500/10 blur-[100px] rounded-full pointer-events-none" />

                <div className="max-w-xl mx-auto mt-10 relative z-10">
                    <div className="text-center mb-10">
                        <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/10 shadow-lg">
                            <ScanLine size={32} className="text-primary-400" />
                        </div>
                        <h1 className="text-3xl font-bold text-white mb-2">Event Check-in Terminal</h1>
                        <p className="text-slate-400">Enter user Ticket ID to verify entry</p>
                    </div>

                    {/* Scanner Input Box */}
                    <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
                        <form onSubmit={handleCheckIn} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-2">Ticket ID</label>
                                <input
                                    type="text"
                                    value={ticketId}
                                    onChange={(e) => setTicketId(e.target.value)}
                                    placeholder="e.g. SELF-170..."
                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-4 text-white text-lg font-mono focus:outline-none focus:border-primary-500 transition-colors placeholder:text-slate-600"
                                    autoFocus
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={status === 'LOADING'}
                                className="w-full py-4 bg-primary-500 hover:bg-primary-600 text-slate-900 rounded-xl font-bold text-lg transition-all shadow-lg shadow-primary-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                {status === 'LOADING' ? (
                                    <span className="animate-pulse">Verifying...</span>
                                ) : (
                                    "Verify & Check In"
                                )}
                            </button>
                        </form>
                    </div>

                    {/* Result Display */}
                    {status === 'SUCCESS' && result && (
                        <div className="mt-8 animate-in slide-in-from-bottom-4 fade-in duration-300">
                            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-6 text-center">
                                <div className="w-12 h-12 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-3 shadow-lg shadow-emerald-500/30">
                                    <CheckCircle2 size={24} className="text-slate-900" />
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-1">Access Granted</h3>
                                <p className="text-emerald-400 font-medium mb-4">Checked in successfully</p>

                                <div className="bg-black/20 rounded-xl p-4 text-left space-y-2">
                                    <div className="flex items-center gap-3">
                                        <User size={16} className="text-slate-400" />
                                        <span className="text-white font-medium">{result.attendee}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <ScanLine size={16} className="text-slate-400" />
                                        <span className="text-slate-300 text-sm">{result.event}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {status === 'ERROR' && (
                        <div className="mt-8 animate-in slide-in-from-bottom-4 fade-in duration-300">
                            <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 text-center">
                                <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-3 shadow-lg shadow-red-500/30">
                                    <XCircle size={24} className="text-white" />
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-1">Access Denied</h3>
                                <p className="text-red-400 font-medium">{errorMsg}</p>
                            </div>
                        </div>
                    )}

                    {/* Recent Scans List */}
                    {recentScans.length > 0 && (
                        <div className="mt-12">
                            <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Recent Scans</h3>
                            <div className="space-y-3">
                                {recentScans.map((scan, i) => (
                                    <div key={i} className="flex items-center justify-between p-4 bg-white/5 border border-white/5 rounded-xl">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-xs text-slate-400">
                                                {i + 1}
                                            </div>
                                            <div>
                                                <div className="text-white font-medium text-sm">{scan.name}</div>
                                                <div className="text-xs text-slate-500">{scan.id}</div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-slate-500">
                                            <Clock size={12} />
                                            {scan.time}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                </div>
            </main>
        </div>
    );
}
