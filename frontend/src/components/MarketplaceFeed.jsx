import React from 'react';
import { toPng } from 'https://esm.sh/html-to-image';
import { useRef } from 'react';

export const MarketplaceFeed = ({ events = [], onEventClick }) => {
    // Process events for display
    const items = events.slice(0, 15).map(event => ({
        id: event.id,
        title: event.title,
        location: event.venue_name || 'Chennai Hub',
        date: new Date(event.start_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
        image: event.image_url || `https://images.unsplash.com/photo-1540575861501-7ad05823c9f5?q=80&w=2070&auto=format&fit=crop`,
        isTrending: (event.capacity || 0) > 100,
        raw: event
    }));

    return (
        <section className="py-4 border-t border-slate-100">
            <div className="flex items-end justify-between mb-6">
                <div>
                    <h2 className="text-sm font-black uppercase tracking-[0.3em] text-indigo-500 mb-4">Discovery Marketplace</h2>
                    <h3 className="text-4xl font-black text-slate-900 tracking-tight">Every Event in One Hub</h3>
                    <p className="text-slate-500 font-medium mt-1">Live, verified opportunities across the Chennai ecosystem.</p>
                </div>
                <div className="hidden md:block">
                    <span className="text-xs font-black text-slate-400 uppercase tracking-widest">{items.length} Active Nodes</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {items.length === 0 ? (
                    <div className="col-span-full py-20 text-center bg-slate-50 rounded-[2.5rem] border border-dashed border-slate-200">
                        <p className="text-slate-400 font-medium italic">Synchronizing with ecosystem nodes... no events found yet.</p>
                    </div>
                ) : (
                    items.map((item, idx) => (
                        <FeedItem key={item.id} item={item} idx={idx} onClick={() => onEventClick && onEventClick(item.raw)} />
                    ))
                )}
            </div>
        </section>
    );
};

const FeedItem = ({ item, idx, onClick }) => {
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
        <div
            className="group cursor-pointer flex flex-col bg-white rounded-[2.5rem] hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-300 border border-slate-100/50"
            onClick={onClick}
        >
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
