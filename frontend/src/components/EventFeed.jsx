import { useState } from 'react';
import { Search, MapPin, Calendar, ExternalLink, ArrowLeft, Eye } from 'lucide-react';
import EventDetailModal from './EventDetailModal';

export default function EventFeed({ events, loading, error, onBack }) {
  const [search, setSearch] = useState("");
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false);

  const handleEventClick = (event) => {
    // Always open modal for consistent experience
    setSelectedEvent(event);
    setIsModalOpen(true);
    setIsRegistered(false);
  };

  const handleExternalRedirect = async (event) => {
    // 1. Track Click
    try {
      await fetch('/api/v1/track-click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_id: event.id,
          user_email: "guest@example.com"
        })
      });
    } catch (e) { console.error(e); }

    // 2. Redirect
    window.open(event.url, '_blank');
  };

  const handleInternalRegister = async (event, payload = null) => {
    try {
      const res = await fetch(`/api/v1/events/${event.id}/register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload || {})
      });

      if (res.ok) {
        setIsRegistered(true);
        // alert("Registered Successfully!"); // integrated into modal UI
      } else {
        const data = await res.json();
        if (data.status === "ALREADY_REGISTERED") {
          setIsRegistered(true);
        } else {
          alert("Registration failed: " + (typeof data.detail === 'object' ? JSON.stringify(data.detail) : (data.detail || "Unknown error")));
        }
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong with registration.");
    }
  };

  const filtered = events.filter(e =>
    e.title.toLowerCase().includes(search.toLowerCase()) ||
    e.venue_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-4">
            {onBack && (
              <button onClick={onBack} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
                <ArrowLeft size={24} />
              </button>
            )}
            <div>
              <h1 className="text-3xl font-bold text-white">All Events</h1>
              <p className="text-slate-400">Browse {events.length} upcoming events in Chennai</p>
            </div>
          </div>
          <div className="relative w-full md:w-auto">
            <Search className="absolute left-3 top-3 text-slate-500" size={20} />
            <input
              type="text"
              placeholder="Search events..."
              className="bg-slate-900 border border-slate-800 rounded-full py-2 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-primary-500 w-full md:w-80 text-slate-200 placeholder-slate-500"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </header>

        {error && (
          <div className="bg-red-500/10 text-red-200 p-4 rounded-lg mb-6 border border-red-500/20">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-20 animate-pulse text-primary-400">Loading Events...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map(event => (
              <div key={event.id} className="bg-slate-900 rounded-xl overflow-hidden hover:shadow-xl hover:shadow-primary-500/10 transition-all border border-slate-800 group hover:-translate-y-1">
                <div className="h-48 bg-slate-800 relative overflow-hidden">
                  {event.image_url ? (
                    <img src={event.image_url} alt={event.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-600 bg-slate-800">
                      <Calendar size={48} opacity={0.2} />
                    </div>
                  )}
                  <div className="absolute top-3 right-3 bg-slate-950/90 px-3 py-1 rounded-full text-xs font-bold text-primary-400 border border-primary-500/20 backdrop-blur-sm">
                    {event.is_free ? 'FREE' : 'PAID'}
                  </div>
                </div>

                <div className="p-5 flex-1 flex flex-col">
                  <h3 className="text-lg font-bold mb-3 text-white line-clamp-2 leading-tight min-h-[3rem]" title={event.title}>{event.title}</h3>

                  <div className="space-y-3 text-sm text-slate-400 mb-6 flex-1">
                    <div className="flex items-center gap-3">
                      <div className="p-1.5 bg-slate-800 rounded-lg text-primary-500">
                        <Calendar size={14} />
                      </div>
                      <span className="font-medium">{new Date(event.start_time).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="p-1.5 bg-slate-800 rounded-lg text-primary-500">
                        <MapPin size={14} />
                      </div>
                      <span className="line-clamp-1">{event.venue_name}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleEventClick(event)}
                    className="w-full bg-primary-600 hover:bg-primary-500 text-white font-medium py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-primary-500/25 active:scale-95"
                  >
                    <span>
                      {(event.raw_data?.source === 'InfiniteBZ' || event.url?.includes('infinitebz.com'))
                        ? 'View'
                        : 'Register Now'}
                    </span>
                    {(event.raw_data?.source === 'InfiniteBZ' || event.url?.includes('infinitebz.com'))
                      ? <Eye size={16} />
                      : <ExternalLink size={16} />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
        <EventDetailModal
          event={selectedEvent}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onRegister={handleInternalRegister}
          isRegistered={isRegistered}
        />
      </div>
    </div >
  )
}
