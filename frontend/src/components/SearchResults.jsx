import React, { useRef } from 'react';
import { toPng } from 'html-to-image';
import { ArrowLeft, Search } from 'lucide-react';

export const SearchResults = ({ events = [], query, onClear, loading, onEventClick }) => {
    // Filter events based on query if not already filtered by backend
    // Since we are moving to backend search, we trust 'events' is the result set.
    // However, keeping the filter as a fallback or for client-side refining is okay, 
    // but better to just show 'events'.
    const results = events.map(event => ({
        id: event.id,
        title: event.title,
        matchScore: 85 + Math.floor(Math.random() * 14), // dynamic mock
        rating: (4.5 + Math.random() * 0.4).toFixed(1),
        location: event.venue_name || 'Chennai Hub',
        date: new Date(event.start_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
        attendees: event.capacity || 100,
        image: event.image_url || `https://images.unsplash.com/photo-1540575861501-7ad05823c9f5?q=80&w=2070&auto=format&fit=crop`,
        isTrending: (event.capacity || 0) > 100,
        raw: event
    }));

    return (
        <div className="min-h-screen bg-[#fdfdff] pt-10 px-4 md:px-8 pb-20 animate-in fade-in duration-500">
            <div className="max-w-7xl mx-auto">
                <div className="flex items-center gap-4 mb-8">
                    <button
                        onClick={onClear}
                        className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-500 hover:text-indigo-600"
                    >
                        <ArrowLeft size={24} />
                    </button>
                    <div>
                        <h2 className="text-3xl font-black text-slate-900 tracking-tight">Search Results</h2>
                        <p className="text-slate-500 mt-1">Found {loading ? '...' : results.length} events for "{query}"</p>
                    </div>
                </div>

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                        <p className="text-slate-500 mt-4 font-medium">Searching database...</p>
                    </div>
                ) : results.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mb-6 text-slate-300">
                            <Search size={48} />
                        </div>
                        <h3 className="text-xl font-bold text-slate-900 mb-2">No matching events found</h3>
                        <p className="text-slate-500 max-w-md mx-auto">
                            Try adjusting your search terms or browse our curated collections.
                        </p>
                        <button
                            onClick={onClear}
                            className="mt-8 px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-500/20 hover:bg-indigo-700 transition-all"
                        >
                            Back to All Events
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {results.map((item, idx) => (
                            <ResultCard key={item.id} item={item} idx={idx} onClick={() => onEventClick && onEventClick(item.raw)} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

const ResultCard = ({ item, idx, onClick }) => {
    const cardRef = useRef(null);

    const downloadAsPng = async (e) => {
        e.stopPropagation();
        if (cardRef.current === null) return;
        try {
            const dataUrl = await toPng(cardRef.current, { cacheBust: true, backgroundColor: '#ffffff', pixelRatio: 2 });
            const link = document.createElement('a');
            link.download = `event-${item.id}.png`;
            link.href = dataUrl;
            link.click();
        } catch (err) {
            console.error('Failed to export card', err);
        }
    };

    return (
        <div ref={cardRef} onClick={onClick} className="group cursor-pointer flex flex-col bg-white rounded-[2.5rem] hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-300 border border-slate-100/50">
            <div className="relative aspect-[16/10] overflow-hidden rounded-[2.5rem] mb-6 bg-slate-100 m-2">
                <img
                    src={item.image}
                    className="w-full h-full object-cover transition-transform duration-[4s] ease-out group-hover:scale-125 group-hover:rotate-1"
                    alt={item.title}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>


            </div>

            <div className="flex flex-col flex-1 px-6 pb-6">
                <div className="flex items-center gap-3 mb-2">
                    <span className="text-xs font-black text-indigo-600 uppercase tracking-widest">{item.date}</span>
                    <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                    <span className="text-xs font-bold text-slate-400">{item.location}</span>
                </div>

                <h3 className="text-xl font-black text-slate-900 group-hover:text-indigo-600 transition-colors mb-4 leading-tight tracking-tight line-clamp-2">
                    {item.title}
                </h3>

                <div className="mt-auto pt-4"></div>
            </div>
        </div>
    );
};
