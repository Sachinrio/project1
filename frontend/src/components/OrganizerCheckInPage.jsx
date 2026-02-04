
import React, { useState, useEffect } from 'react';
import QrScanner from 'react-qr-scanner';
import { ChevronLeft, Camera, CheckCircle2, XCircle, Search, RefreshCw } from 'lucide-react';

export default function OrganizerCheckInPage({ eventId, onNavigate }) {
    console.log("OrganizerCheckInPage Rendered with eventId:", eventId);
    const [scanResult, setScanResult] = useState(null);
    const [manualId, setManualId] = useState('');
    const [status, setStatus] = useState(null); // 'scanning', 'processing', 'success', 'error', 'already_checked_in'
    const [attendee, setAttendee] = useState(null);
    const [message, setMessage] = useState('');
    const [cameraActive, setCameraActive] = useState(false);

    const handleScan = (data) => {
        if (data && status !== 'processing' && status !== 'success' && status !== 'already_checked_in' && cameraActive) {
            // The library returns an object or string depending on version, usually data.text
            const text = data?.text || data;
            if (text) {
                handleCheckIn(text);
            }
        }
    };

    const handleError = (err) => {
        console.error(err);
    };

    const handleCheckIn = async (ticketId) => {
        // If it's a full URL or text, try to extract ID or just send it (assuming standard format "Ticket ID: SELF-...")
        // Our QR generation logic: f"Ticket ID: {registration.confirmation_id}\nEvent..."
        // We should be robust.

        setStatus('processing');
        setCameraActive(false); // Pause camera

        let finalId = ticketId;
        // Extract ID if full text provided
        if (ticketId.includes("Ticket ID: ")) {
            const match = ticketId.match(/Ticket ID: ([^\n]+)/);
            if (match && match[1]) finalId = match[1].trim();
        }

        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/v1/events/${activeEventId}/check-in?ticket_id=${finalId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await res.json();

            if (res.ok && data.status === 'SUCCESS') {
                setStatus('success');
                setAttendee(data.attendee);
                setMessage(data.message);
            } else if (data.status === 'ALREADY_CHECKED_IN') {
                setStatus('already_checked_in');
                setAttendee(data.attendee);
                setMessage(data.message);
            } else {
                setStatus('error');
                setMessage(data.message || 'Invalid Ticket');
                setAttendee(null);
            }

        } catch (err) {
            console.error(err);
            setStatus('error');
            setMessage('Network error. Please try again.');
        }
    };

    const resetScanner = () => {
        setStatus('scanning');
        setScanResult(null);
        setAttendee(null);
        setMessage('');
        setManualId('');
        setCameraActive(true);
    };

    // Start camera on load
    useEffect(() => {
        setCameraActive(true);
        setStatus('scanning');
        return () => setCameraActive(false);
    }, []);

    const [events, setEvents] = useState([]);
    const [loadingEvents, setLoadingEvents] = useState(false);
    const [internalEventId, setInternalEventId] = useState(null);

    const activeEventId = eventId || internalEventId;

    useEffect(() => {
        if (!activeEventId) {
            fetchEvents();
        }
    }, [activeEventId]);

    const fetchEvents = async () => {
        setLoadingEvents(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/events', {
                headers: token ? { 'Authorization': `Bearer ${token}` } : {}
            });
            if (res.ok) {
                const data = await res.json();
                // Handle different response structures if needed
                const eventList = Array.isArray(data) ? data : (data.data || []);
                setEvents(eventList);
            }
        } catch (err) {
            console.error("Failed to load events", err);
        } finally {
            setLoadingEvents(false);
        }
    };

    if (!activeEventId) {
        return (
            <div className="min-h-screen bg-slate-900 text-white p-4">
                {/* Header */}
                <div className="flex items-center gap-4 mb-6">
                    <button onClick={() => onNavigate('dashboard')} className="p-2 bg-slate-800 rounded-full hover:bg-slate-700">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">Select Event to Scan</h1>
                </div>

                <div className="max-w-md mx-auto">
                    {loadingEvents ? (
                        <div className="text-center text-slate-400 py-10">Loading events...</div>
                    ) : (
                        <div className="space-y-3">
                            {events.length === 0 ? (
                                <div className="text-center text-slate-500 py-10">No events found.</div>
                            ) : (
                                events.map(event => (
                                    <div
                                        key={event.id}
                                        onClick={() => setInternalEventId(event.id)}
                                        className="bg-slate-800 border border-slate-700 p-4 rounded-xl hover:border-primary-500 hover:bg-slate-700/50 cursor-pointer transition-all flex items-center justify-between group"
                                    >
                                        <div>
                                            <h3 className="font-bold text-white mb-1 group-hover:text-primary-400 transition-colors">{event.title}</h3>
                                            <p className="text-xs text-slate-400">{new Date(event.start_time).toLocaleDateString()}</p>
                                        </div>
                                        <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-slate-500 group-hover:bg-primary-500 group-hover:text-slate-900 transition-colors">
                                            <Camera size={16} />
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-900 text-white p-4">
            {/* Header */}
            <div className="flex items-center gap-4 mb-6">
                <button onClick={() => onNavigate('dashboard')} className="p-2 bg-slate-800 rounded-full hover:bg-slate-700">
                    <ChevronLeft size={24} />
                </button>
                <h1 className="text-xl font-bold">Organizer Check-in</h1>
            </div>

            <div className="max-w-md mx-auto space-y-6">

                {/* Verification Status Card */}
                {status === 'success' && (
                    <div className="bg-green-600/20 border border-green-500 rounded-2xl p-6 text-center animate-in fade-in zoom-in duration-300">
                        <CheckCircle2 size={64} className="mx-auto text-green-400 mb-4" />
                        <h2 className="text-2xl font-bold text-green-400 mb-2">Verified!</h2>
                        <div className="bg-slate-800/50 rounded-xl p-4 mt-4">
                            <p className="text-sm text-slate-400">Attendee</p>
                            <p className="text-xl font-bold">{attendee?.name}</p>
                            <p className="text-slate-300">{attendee?.email}</p>
                        </div>
                        <div className="mt-2 text-green-200 text-sm">{attendee?.ticket_type}</div>
                        <button onClick={resetScanner} className="mt-6 w-full py-3 bg-white text-green-800 font-bold rounded-xl shadow-lg hover:bg-green-50">
                            Scan Next
                        </button>
                    </div>
                )}

                {status === 'already_checked_in' && (
                    <div className="bg-yellow-600/20 border border-yellow-500 rounded-2xl p-6 text-center animate-in fade-in zoom-in duration-300">
                        <RefreshCw size={64} className="mx-auto text-yellow-400 mb-4" />
                        <h2 className="text-xl font-bold text-yellow-400 mb-2">Already Checked In</h2>
                        <p className="text-yellow-200 mb-4">{message}</p>
                        <div className="bg-slate-800/50 rounded-xl p-4 mt-4 text-left">
                            <p className="text-sm text-slate-400">Original Attendee</p>
                            <p className="text-lg font-bold">{attendee?.name}</p>
                            <p className="text-slate-300 text-sm">{attendee?.ticket_type}</p>
                        </div>
                        <button onClick={resetScanner} className="mt-6 w-full py-3 bg-white text-yellow-800 font-bold rounded-xl shadow-lg hover:bg-yellow-50">
                            Scan Next
                        </button>
                    </div>
                )}

                {status === 'error' && (
                    <div className="bg-red-600/20 border border-red-500 rounded-2xl p-6 text-center animate-in fade-in zoom-in duration-300">
                        <XCircle size={64} className="mx-auto text-red-400 mb-4" />
                        <h2 className="text-2xl font-bold text-red-400 mb-2">Invalid Ticket</h2>
                        <p className="text-red-200 mb-6">{message}</p>
                        <button onClick={resetScanner} className="w-full py-3 bg-white text-red-800 font-bold rounded-xl shadow-lg hover:bg-red-50">
                            Try Again
                        </button>
                    </div>
                )}

                {/* Scanner & Manual Input */}
                {(status === 'scanning' || status === 'processing') && (
                    <>
                        <div className="bg-black rounded-3xl overflow-hidden aspect-square relative shadow-2xl border border-slate-700">
                            {cameraActive && (
                                <QrScanner
                                    delay={300}
                                    onError={handleError}
                                    onScan={handleScan}
                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                    constraints={{
                                        video: { facingMode: 'environment' } // Use Back Camera
                                    }}
                                />
                            )}
                            <div className="absolute inset-0 border-2 border-primary-500/50 pointer-events-none flex items-center justify-center">
                                <div className="w-64 h-64 border-2 border-primary-500 rounded-lg relative">
                                    <div className="absolute top-0 left-0 w-4 h-4 border-t-4 border-l-4 border-primary-500 -mt-1 -ml-1"></div>
                                    <div className="absolute top-0 right-0 w-4 h-4 border-t-4 border-r-4 border-primary-500 -mt-1 -mr-1"></div>
                                    <div className="absolute bottom-0 left-0 w-4 h-4 border-b-4 border-l-4 border-primary-500 -mb-1 -ml-1"></div>
                                    <div className="absolute bottom-0 right-0 w-4 h-4 border-b-4 border-r-4 border-primary-500 -mb-1 -mr-1"></div>
                                </div>
                            </div>
                            {status === 'processing' && (
                                <div className="absolute inset-0 bg-black/60 flex items-center justify-center backdrop-blur-sm">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
                                </div>
                            )}
                        </div>

                        <div className="text-center text-slate-400 text-sm">
                            Point camera at QR code
                        </div>

                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-5 w-5 text-gray-400" />
                            </div>
                            <input
                                type="text"
                                placeholder="Or enter Ticket ID manually..."
                                className="block w-full pl-10 pr-4 py-3 bg-slate-800 border-slate-700 text-white rounded-xl focus:ring-primary-500 focus:border-primary-500"
                                value={manualId}
                                onChange={(e) => setManualId(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleCheckIn(manualId)}
                            />
                            {manualId && (
                                <button
                                    onClick={() => handleCheckIn(manualId)}
                                    className="absolute right-2 top-2 bottom-2 bg-primary-500 text-slate-900 px-4 rounded-lg font-bold text-sm"
                                >
                                    Check
                                </button>
                            )}
                        </div>
                    </>
                )}

            </div>
        </div>
    );
}
