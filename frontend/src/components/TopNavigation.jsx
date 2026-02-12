import React, { useState, useEffect } from 'react';
import { Search, LogIn, UserPlus, Bell, Calendar, MapPin, Clock } from 'lucide-react';

export const TopNavigation = ({ onLogin, onSignup, user, events = [], onSearch }) => {
    const [hasNotifications, setHasNotifications] = useState(false);
    const [showNotifications, setShowNotifications] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        const checkNotifications = () => {
            if (!events.length) return;

            const lastViewed = localStorage.getItem('notificationLastViewed');
            // Find the most recent event creation time
            // Assuming events have 'created_at' or we use 'start_time' as a proxy if created_at is missing
            // But checking schema, 'created_at' exists.
            const latestEvent = events.reduce((latest, current) => {
                return new Date(current.created_at || current.start_time) > new Date(latest.created_at || latest.start_time) ? current : latest;
            }, events[0]);

            if (!latestEvent) return;

            const latestEventTime = new Date(latestEvent.created_at || latestEvent.start_time).getTime();
            const lastViewedTime = lastViewed ? new Date(lastViewed).getTime() : 0;

            if (latestEventTime > lastViewedTime) {
                setHasNotifications(true);
            }
        };

        checkNotifications();
    }, [events]);

    const handleNotificationClick = () => {
        setShowNotifications(!showNotifications);
        if (!showNotifications) {
            setHasNotifications(false);
            localStorage.setItem('notificationLastViewed', new Date().toISOString());
        }
    };

    // Sort events by creation date for notification feed
    const recentEvents = [...events].sort((a, b) =>
        new Date(b.created_at || b.start_time) - new Date(a.created_at || a.start_time)
    ).slice(0, 5);

    const handleSearchSubmit = (e) => {
        if (e.key === 'Enter' || e.type === 'click') {
            if (onSearch) {
                onSearch(searchQuery);
            }
        }
    };

    return (
        <div className="sticky top-0 z-40 bg-white/80 backdrop-blur-md flex items-center justify-between px-8 py-4 mb-0 border-b border-fuchsia-100/50">
            {/* Search Bar - Reduced size and centered */}
            <div className="flex-1 flex justify-center max-w-2xl">
                <div className="w-full relative group flex items-center bg-white border border-slate-200 rounded-full p-1.5 shadow-sm hover:shadow-md transition-all">
                    {/* Search Input */}
                    <div className="flex-1 flex items-center px-4">
                        <input
                            type="text"
                            placeholder="Search events..."
                            className="w-full bg-transparent border-none focus:outline-none text-slate-700 placeholder:text-slate-400 text-sm font-medium"
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value);
                                if (onSearch) onSearch(e.target.value);
                            }}
                            onKeyDown={handleSearchSubmit}
                        />
                    </div>



                    {/* Location Display */}
                    <div className="hidden sm:flex items-center px-4 w-48 text-slate-600 font-bold text-sm whitespace-nowrap cursor-pointer hover:text-fuchsia-600 transition-colors border-l border-slate-200 h-full">
                        Chennai, IN
                    </div>

                    {/* Search Button */}
                    <button
                        onClick={handleSearchSubmit}
                        className="bg-fuchsia-600 text-white p-3 rounded-full hover:bg-fuchsia-700 transition-colors shadow-lg shadow-fuchsia-600/20"
                    >
                        <Search size={18} />
                    </button>
                </div>
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center gap-4 ml-8 relative">
                <button
                    onClick={onSignup}
                    className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl font-bold text-sm hover:bg-slate-800 transition-all shadow-lg shadow-slate-900/20"
                >
                    <UserPlus size={18} />
                    <span>Sign Up</span>
                </button>
                {user ? (
                    <div
                        onClick={onLogin}
                        className="flex flex-col items-center cursor-pointer group"
                    >
                        <div className="w-10 h-10 rounded-full bg-slate-900 flex items-center justify-center text-white font-bold shadow-md group-hover:scale-105 transition-transform">
                            {user.email?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <span className="text-[10px] font-bold text-slate-500 mt-1 max-w-[100px] truncate group-hover:text-slate-900 transition-colors">
                            {user.email}
                        </span>
                    </div>
                ) : (
                    <button
                        onClick={onLogin}
                        className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl font-bold text-sm hover:bg-slate-800 transition-all shadow-lg shadow-slate-900/20"
                    >
                        <LogIn size={18} />
                        <span>Log In</span>
                    </button>
                )}
            </div>
        </div>
    );
};
