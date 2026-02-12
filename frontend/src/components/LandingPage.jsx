import React, { useRef, useState, useEffect } from 'react';
import { toPng } from 'html-to-image';
import { PublicSidebar } from './PublicSidebar';
import { TopNavigation } from './TopNavigation';
import { Hero } from './Hero';
import { StrategicOpportunities } from './StrategicOpportunities';
import { CategoriesGrid } from './CategoriesGrid';
import { EcosystemHighlights } from './EcosystemHighlights';
import { CTASection } from './CTASection';
import { Footer } from './Footer';
import { AIInsights } from './AIInsights';
import { IntroAnimation } from './IntroAnimation';
import { SearchResults } from './SearchResults';
import { MarketplaceFeed } from './MarketplaceFeed';

import EventDetailModal from './EventDetailModal';

// LandingPage component replaces the old design with the new component-based architecture
export default function LandingPage({ onNavigate, onLogin, onSignup, events, user }) {
    const rootRef = useRef(null);
    const feedRef = useRef(null);
    const summitRef = useRef(null);
    const networkRef = useRef(null); // New ref for Network section
    const [showIntro, setShowIntro] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);

    const [allEvents, setAllEvents] = useState([]);

    // Event Details Modal State
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [isDetailOpen, setIsDetailOpen] = useState(false);

    useEffect(() => {
        // Fetch ALL events for accurate stats, independent of parent props
        const fetchAllEvents = async () => {
            try {
                const res = await fetch('/api/v1/events?limit=500');
                const data = await res.json();
                if (data && Array.isArray(data.data)) {
                    setAllEvents(data.data);
                } else if (Array.isArray(data)) {
                    setAllEvents(data);
                }
            } catch (err) {
                console.error("Failed to fetch all events for stats", err);
            }
        };
        fetchAllEvents();
    }, []);

    // Use allEvents for calculations if available, falling back to props
    const displayEvents = allEvents.length > 0 ? allEvents : events;

    useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (searchQuery) {
                setIsSearching(true);
                try {
                    const res = await fetch(`/api/v1/events?search=${encodeURIComponent(searchQuery)}`);
                    const data = await res.json();
                    // Handle response structure { data: [], total: ... }
                    setSearchResults(data.data || []);
                } catch (error) {
                    console.error("Search failed", error);
                    setSearchResults([]);
                } finally {
                    setIsSearching(false);
                }
            } else {
                setSearchResults([]);
            }
        }, 500); // 500ms debounce

        return () => clearTimeout(delayDebounceFn);
    }, [searchQuery]);

    const exportPageAsPng = async () => {
        if (rootRef.current === null) return;
        try {
            const dataUrl = await toPng(rootRef.current, { cacheBust: true, backgroundColor: '#fdfdff' });
            const link = document.createElement('a');
            link.download = 'infinite-bz-snapshot.png';
            link.href = dataUrl;
            link.click();
        } catch (err) {
            console.error('Export failed', err);
        }
    };

    const scrollToFeed = () => {
        if (feedRef.current) {
            feedRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const scrollToSummit = () => {
        if (summitRef.current) {
            summitRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    };

    const scrollToNetwork = () => {
        if (networkRef.current) {
            networkRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    };

    const handleEventClick = (event) => {
        setSelectedEvent(event);
        setIsDetailOpen(true);
    };

    return (
        <>
            {showIntro && <IntroAnimation onComplete={() => setShowIntro(false)} />}
            <div ref={rootRef} className={`landing-page-mode flex min-h-screen transition-opacity duration-1000 ${showIntro ? 'opacity-0 overflow-hidden h-screen' : 'opacity-100'}`}>
                {/* Sidebar Navigation */}
                <PublicSidebar onLogin={onLogin} onSignup={onSignup} onDiscover={scrollToFeed} onSummit={scrollToSummit} onNetwork={scrollToNetwork} />

                {/* Main Content Area - Offset for Sidebar */}
                <div className="flex-1 flex flex-col pl-20 lg:pl-64 transition-all duration-300">
                    <TopNavigation
                        onLogin={onLogin}
                        onSignup={onSignup}
                        user={user}
                        events={events}
                        onSearch={(query) => setSearchQuery(query)}
                    />

                    <main className="flex-grow">
                        {searchQuery ? (
                            <SearchResults
                                events={searchResults}
                                query={searchQuery}
                                onClear={() => setSearchQuery("")}
                                loading={isSearching}
                                onEventClick={handleEventClick}
                            />
                        ) : (
                            <>
                                <Hero events={events} onLogin={onLogin} onExplore={scrollToFeed} />

                                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
                                    {/* Section Header: Categories */}
                                    <div className="mb-6">
                                        <div className="flex items-center justify-between mb-8">
                                            <div>
                                                <h2 className="text-sm font-black uppercase tracking-[0.2em] text-indigo-500 mb-2">Industries</h2>
                                                <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">Browse Chennai's Core Hubs</h3>
                                            </div>
                                        </div>
                                        <CategoriesGrid events={displayEvents} onEventClick={handleEventClick} />
                                    </div>

                                    <div className="mb-12">
                                        <div className="flex items-end justify-between mb-8 border-b border-slate-100 pb-6">
                                            <div>
                                                <h2 className="text-3xl font-black text-slate-900 tracking-tight">Strategic Matches</h2>
                                                <p className="text-slate-500 font-medium mt-1">Founders, capital, and talent tuned to your goals.</p>
                                            </div>
                                        </div>
                                        <StrategicOpportunities events={events} onEventClick={handleEventClick} />
                                    </div>

                                    <div className="flex flex-col lg:flex-row gap-10 mt-12">
                                        {/* Primary Feed */}
                                        <div className="flex-1 space-y-2">


                                            <section ref={networkRef}>
                                                <EcosystemHighlights />
                                            </section>
                                        </div>
                                        {/* Side-Scout Panel */}
                                        <aside className="lg:w-96 space-y-12">
                                            <div className="sticky top-28 space-y-12">
                                                <AIInsights />

                                                <div ref={summitRef} className="bg-slate-900 p-10 rounded-[2.5rem] text-white shadow-2xl shadow-indigo-200/20 group relative overflow-hidden">
                                                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-cyan-500"></div>
                                                    <h4 className="text-2xl font-black mb-4 group-hover:text-indigo-400 transition-colors">Host a Summit</h4>
                                                    <p className="text-slate-400 text-sm mb-8 leading-relaxed font-medium">Connect your brand with Chennai's fastest-growing venture community.</p>
                                                    <button onClick={onSignup} className="bg-white text-slate-950 px-8 py-4 rounded-2xl font-black text-sm hover:bg-indigo-500 hover:text-white transition-all btn-bounce w-full">
                                                        Create Event
                                                    </button>
                                                </div>
                                            </div>
                                        </aside>
                                    </div>
                                    {/* Moved MarketplaceFeed to Bottom (Full Width) */}
                                    <div ref={feedRef} className="mt-12">
                                        <MarketplaceFeed events={events} onEventClick={handleEventClick} />
                                        <div />
                                    </div>
                                </div>

                                <CTASection onLogin={onLogin} onSignup={onSignup} />
                            </>
                        )}
                    </main>

                    <Footer />
                </div>
            </div>

            {/* Global Event Detail Modal */}
            <EventDetailModal
                event={selectedEvent}
                isOpen={isDetailOpen}
                onClose={() => setIsDetailOpen(false)}
                user={user}
                onLogin={onLogin}
                onRegister={() => {
                    setIsDetailOpen(false);
                    // Registration logic handled by CheckoutModal internally mostly, 
                    // but this callback is for post-registration actions if needed.
                }}
                isRegistered={false} // Would need real logic to check if user is registered
            />
        </>
    );
}

const PulseItem = ({ label, value, trend, isSpecial }) => (
    <div className="flex justify-between items-center group cursor-default">
        <div>
            <p className="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-0.5">{label}</p>
            <p className="text-xl font-black text-slate-900 group-hover:text-indigo-600 transition-colors">{value}</p>
        </div>
        <span className={`px-2 py-1 rounded-lg text-[9px] font-black uppercase tracking-tighter ${isSpecial ? 'bg-indigo-600 text-white' : trend.includes('+') ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-400'
            }`}>
            {trend}
        </span>
    </div>
);
