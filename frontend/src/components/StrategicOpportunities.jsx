
import React, { useRef } from 'react';
import { toPng } from 'https://esm.sh/html-to-image';

export const StrategicOpportunities = ({ events = [], onEventClick }) => {
    // prioritize InfiniteBZ events
    const sortedEvents = [...(events || [])].sort((a, b) => {
        const sourceA = a.raw_data?.source === 'InfiniteBZ' ? 1 : 0;
        const sourceB = b.raw_data?.source === 'InfiniteBZ' ? 1 : 0;
        return sourceB - sourceA; // InfiniteBZ first
    });

    // Map real events to opportunity format (show 6)
    const opportunities = sortedEvents.slice(0, 6).map(event => ({
        id: event.id,
        title: event.title,
        // Mocking some matchmaking data for now as backend doesn't provide it yet
        matchScore: 85 + Math.floor(Math.random() * 14),
        rating: (4.5 + Math.random() * 0.4).toFixed(1),
        location: event.venue_name || 'Chennai Hub',
        date: new Date(event.start_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
        attendees: event.capacity || 100,
        image: event.image_url || `https://images.unsplash.com/photo-1540575861501-7ad05823c9f5?q=80&w=2070&auto=format&fit=crop`,
        isTrending: (event.capacity || 0) > 100,
        raw: event // Pass raw event for click handler
    }));

    if (opportunities.length === 0) {
        return <div className="text-slate-500">No strategic matches found at the moment.</div>;
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-6">
            {opportunities.map((opp, idx) => (
                <OpportunityCard key={opp.id} opp={opp} idx={idx} onClick={() => onEventClick && onEventClick(opp.raw)} />
            ))}
        </div>
    );
};

const OpportunityCard = ({ opp, idx, onClick }) => {
    const cardRef = useRef(null);

    const downloadAsPng = async (e) => {
        e.stopPropagation();
        if (cardRef.current === null) return;
        try {
            const dataUrl = await toPng(cardRef.current, { cacheBust: true, backgroundColor: '#ffffff', pixelRatio: 2 });
            const link = document.createElement('a');
            link.download = `event-${opp.id}.png`;
            link.href = dataUrl;
            link.click();
        } catch (err) {
            console.error('Failed to export card', err);
        }
    };

    return (
        <div ref={cardRef} className="group cursor-pointer flex flex-col bg-white rounded-[2.5rem]" onClick={onClick}>
            <div className="relative aspect-[16/10] overflow-hidden rounded-[2.5rem] mb-8 bg-slate-100 border border-slate-100 shadow-sm transition-all duration-500 group-hover:shadow-2xl group-hover:shadow-indigo-500/20 group-hover:-translate-y-2">
                <img
                    src={opp.image}
                    className="w-full h-full object-cover transition-transform duration-[4s] ease-out group-hover:scale-125 group-hover:rotate-1"
                    alt={opp.title}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>




            </div>

            <div className="flex flex-col flex-1 px-4 pb-4">
                <div className="flex items-center gap-3 mb-3">
                    <span className="text-xs font-black text-indigo-600 uppercase tracking-widest transition-all group-hover:translate-x-1">{opp.date}</span>
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-200"></span>
                    <span className="text-xs font-bold text-slate-400 group-hover:text-slate-600">Limited Capacity</span>
                </div>

                <h3 className="text-2xl font-black text-slate-900 group-hover:text-indigo-600 transition-colors mb-4 leading-tight tracking-tight">
                    {opp.title}
                </h3>

                <div className="mt-auto pt-6"></div>
            </div>
        </div>
    );
};
