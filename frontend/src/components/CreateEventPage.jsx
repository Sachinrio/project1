import { useState } from 'react';
import {
    ChevronLeft, Home, Search, Bell, Settings, LogOut,
    Type, Image as ImageIcon, AlignLeft, Calendar,
    MapPin, Globe, Check, Eye, Tag, Users, Ticket, IndianRupee, Sparkles, Wand2,
    Bold, Italic, Underline, Link as LinkIcon, List, Clock, Plus, Trash2, User, Twitter, Linkedin
} from 'lucide-react';
import Sidebar from './Sidebar';
import TicketManager from './TicketManager';
import MarkdownEditor from './MarkdownEditor';
import ImageGalleryUploader from './ImageGalleryUploader';

export default function CreateEventPage({ user, onNavigate, onLogout, onSave }) {
    console.log("CreateEventPage Rendered");
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        category: "Conference",
        startDate: "",
        startTime: "10:00",
        endDate: "",
        endTime: "12:00",
        mode: "offline",
        location: "",
        imageUrl: "",
        galleryImages: [],
        isFree: true,
        ticketPrice: 0,
        audience: "General Public",
        tags: [],
        capacity: "",
        registrationDeadline: "",
        meetingLink: "",
        meetingLinkPrivate: true,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        agendaItems: [],
        speakers: [],
        tickets: []
    });

    const [loading, setLoading] = useState(false);
    const [isGeneratingAI, setIsGeneratingAI] = useState(false);
    const [showSuccessModal, setShowSuccessModal] = useState(false);
    const [createdEventId, setCreatedEventId] = useState(null);

    const handleAIGenerate = async () => {
        if (!formData.title) {
            alert("Please enter an event title first!");
            return;
        }
        setIsGeneratingAI(true);
        try {
            const payload = {
                title: formData.title,
                category: formData.category,
                start_time: formData.startTime,
                end_time: formData.endTime
            };
            const response = await fetch('/api/v1/ai/generate-event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error("AI Generation failed");
            const data = await response.json();

            setFormData(prev => ({
                ...prev,
                description: data.description || prev.description,
                imageUrl: data.imageUrl || prev.imageUrl,
                tags: data.tags || prev.tags,
                agendaItems: data.agenda?.map((item, idx) => ({
                    id: Date.now() + idx,
                    startTime: item.time || "10:00",
                    endTime: "11:00",
                    title: item.title,
                    description: `Speaker: ${item.speaker}`
                })) || prev.agendaItems,
                aiGenerated: true
            }));
        } catch (err) {
            console.error(err);
            alert("Failed to generate content: " + err.message);
        } finally {
            setIsGeneratingAI(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleTagAdd = (e) => {
        if (e.key === 'Enter' && e.target.value.trim()) {
            if (!formData.tags.includes(e.target.value.trim())) {
                setFormData(prev => ({ ...prev, tags: [...prev.tags, e.target.value.trim()] }));
            }
            e.target.value = '';
        }
    };

    const removeTag = (tag) => {
        setFormData(prev => ({ ...prev, tags: prev.tags.filter(t => t !== tag) }));
    };

    const handleSubmit = async () => {
        setLoading(true);
        const payload = {
            ...formData,
            start_time: `${formData.startDate}T${formData.startTime}:00`,
            end_time: `${formData.endDate || formData.startDate}T${formData.endTime}:00`,
            venue_name: formData.mode === 'online' ? 'Online Event' : formData.location,
            venue_address: formData.mode === 'online' ? 'Online' : formData.location,
            online_event: formData.mode === 'online',
            image_url: formData.imageUrl,
            category: formData.category,
            timezone: formData.timezone,
            agenda: formData.agendaItems,
            speakers: formData.speakers,
            tickets: formData.tickets,
            gallery_images: formData.galleryImages,
            // Calculate capacity from tickets if provided, else use global capacity
            capacity: formData.tickets.length > 0
                ? formData.tickets.reduce((acc, t) => acc + (parseInt(t.quantity) || 0), 0)
                : (formData.capacity ? parseInt(formData.capacity) : null),
            // Determine price/free status from tickets
            is_free: formData.tickets.length > 0 ? formData.tickets.every(t => t.type === 'free' || t.price === 0) : formData.isFree,
            price: formData.tickets.length > 0
                ? (Math.min(...formData.tickets.map(t => parseFloat(t.price) || 0))).toString()
                : (formData.isFree ? "0" : formData.ticketPrice.toString())
        };
        try {
            const result = await onSave(payload);
            if (result && result.eventbrite_id) {
                setCreatedEventId(result.eventbrite_id);
                setShowSuccessModal(true);
            }
        } catch (e) {
            alert(e.message);
        } finally {
            setLoading(false);
        }
    };

    // --- Helpers for Agenda ---
    const addAgendaItem = () => {
        setFormData(prev => ({
            ...prev,
            agendaItems: [
                ...prev.agendaItems,
                { id: Date.now(), startTime: "", endTime: "", title: "", description: "" }
            ]
        }));
    };

    const removeAgendaItem = (id) => {
        setFormData(prev => ({
            ...prev,
            agendaItems: prev.agendaItems.filter(item => item.id !== id)
        }));
    };

    const updateAgendaItem = (id, field, value) => {
        setFormData(prev => ({
            ...prev,
            agendaItems: prev.agendaItems.map(item =>
                item.id === id ? { ...item, [field]: value } : item
            )
        }));
    };

    // --- Helpers for Speakers ---
    const addSpeaker = () => {
        setFormData(prev => ({
            ...prev,
            speakers: [
                ...prev.speakers,
                { id: Date.now(), name: "", role: "", company: "", imageUrl: "", linkedIn: "", twitter: "" }
            ]
        }));
    };

    const removeSpeaker = (id) => {
        setFormData(prev => ({
            ...prev,
            speakers: prev.speakers.filter(item => item.id !== id)
        }));
    };

    const updateSpeaker = (id, field, value) => {
        setFormData(prev => ({
            ...prev,
            speakers: prev.speakers.map(item =>
                item.id === id ? { ...item, [field]: value } : item
            )
        }));
    };

    return (
        <div className="min-h-screen flex font-sans bg-[#F3F4F6]">
            {/* SIDEBAR */}
            <Sidebar
                activePage="create-event"
                onNavigate={onNavigate}
                onLogout={onLogout}
                onCreateClick={() => { }} // Already here
            />

            {/* MAIN CONTENT */}
            <main className="flex-1 lg:ml-64 p-8 pb-40 bg-[#F3F4F6] text-slate-900 min-h-screen relative font-sans selection:bg-fuchsia-100 selection:text-fuchsia-900">

                <header className="flex justify-between items-center mb-10">
                    <div className="flex items-center gap-4 text-sm text-slate-500 font-medium">
                        <div className="p-2 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer" onClick={() => onNavigate('dashboard')}>
                            <Home size={18} />
                        </div>
                        <ChevronLeft size={16} className="text-slate-400" />
                        <span className="cursor-pointer hover:text-fuchsia-600 transition-colors" onClick={() => onNavigate('dashboard')}>Events</span>
                        <ChevronLeft size={16} className="text-slate-400" />
                        <span className="text-slate-900 font-semibold bg-white px-3 py-1 rounded-full text-xs shadow-sm border border-slate-200">Create New</span>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-fuchsia-500 transition-colors" size={16} />
                            <input
                                type="text"
                                placeholder="Search..."
                                className="bg-white border border-slate-200 rounded-full pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-fuchsia-500 focus:ring-4 focus:ring-fuchsia-500/10 w-64 transition-all shadow-sm text-slate-900 placeholder:text-slate-400"
                            />
                        </div>
                        <button className="text-slate-500 hover:text-fuchsia-600 transition-colors relative">
                            <Bell size={20} />
                            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
                        </button>
                        <div className="h-8 w-px bg-slate-200"></div>
                        <div className="flex items-center gap-3">
                            <div className="text-right hidden md:block">
                                <p className="text-sm font-bold text-slate-900 leading-none">{user?.full_name || 'Admin User'}</p>
                                <p className="text-xs text-slate-500 mt-1">Organizer</p>
                            </div>
                            <div className="w-10 h-10 bg-gradient-to-br from-fuchsia-500 to-pink-600 rounded-full flex items-center justify-center font-bold text-white shadow-lg shadow-fuchsia-500/20 ring-2 ring-white cursor-pointer hover:scale-105 transition-transform">
                                {user?.full_name?.[0] || 'A'}
                            </div>
                        </div>
                    </div>
                </header>

                <div className="max-w-6xl mx-auto animate-in slide-in-from-bottom-4 duration-500">
                    <div className="mb-10 flex justify-between items-end">
                        <div>
                            <h1 className="text-4xl font-extrabold text-slate-900 mb-3 tracking-tight">Create Networking Event</h1>
                            <p className="text-slate-500 text-lg max-w-2xl">Launch your event to the Chennai community. High-quality events get featured on the main dashboard.</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-12 gap-8">

                        {/* LEFT COLUMN - FORM (60%) */}
                        <div className="col-span-12 lg:col-span-7 space-y-8">

                            {/* SECTION 1: ESSENTIALS */}
                            <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow hover:shadow-fuchsia-500/5">
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="w-10 h-10 rounded-2xl bg-fuchsia-50 text-fuchsia-600 flex items-center justify-center font-bold text-lg shadow-sm border border-fuchsia-100">1</div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-900">Event Essentials</h3>
                                        <p className="text-sm text-slate-500">The core details that appear on the event card.</p>
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <div className="group space-y-4">
                                        <div className="flex justify-between items-center">
                                            <label className="block text-sm font-bold text-slate-500 uppercase tracking-wider text-[11px]">Event Title</label>
                                            <button
                                                onClick={handleAIGenerate}
                                                disabled={isGeneratingAI || !formData.title}
                                                className={`flex items - center gap - 2 px - 4 py - 2 rounded - xl text - xs font - bold transition - all shadow - sm ${isGeneratingAI
                                                    ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                                                    : 'bg-gradient-to-r from-fuchsia-600 to-pink-600 text-white hover:from-fuchsia-500 hover:to-pink-500 hover:shadow-fuchsia-500/20 active:scale-95'
                                                    } `}
                                            >
                                                {isGeneratingAI ? (
                                                    <><Sparkles size={14} className="animate-spin" /> Generating...</>
                                                ) : (
                                                    <><Sparkles size={14} /> Magic Generate with AI</>
                                                )}
                                            </button>
                                        </div>
                                        <input
                                            name="title"
                                            value={formData.title}
                                            onChange={handleChange}
                                            placeholder="e.g. Chennai Tech Summit 2026"
                                            className="w-full px-0 py-4 bg-transparent border-0 border-b-2 border-slate-200 focus:border-fuchsia-500 focus:ring-0 transition-all font-bold text-3xl placeholder:text-slate-300 text-slate-900"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-bold text-slate-500 mb-2 uppercase tracking-wider text-[11px]">Description</label>
                                        <div className="rounded-xl border border-slate-200 bg-slate-50/50 overflow-hidden focus-within:ring-2 focus-within:ring-fuchsia-500/20 focus-within:border-fuchsia-500 transition-all group">
                                            <MarkdownEditor
                                                value={formData.description}
                                                onChange={(value) => setFormData({ ...formData, description: value })}
                                                placeholder="Describe your event... (Support for Markdown: **bold**, *italic*, # headings, - lists)"
                                                className="text-slate-900 placeholder:text-slate-400"
                                            />
                                            <div className="text-right px-4 py-2 text-[10px] font-bold uppercase text-slate-400 border-t border-slate-200 bg-slate-50/50">
                                                {formData.description.length}/2000 characters
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-bold text-slate-500 mb-2 uppercase tracking-wider text-[11px]">Cover Image</label>
                                        <div
                                            onClick={() => document.getElementById('fileInput').click()}
                                            className="relative border-2 border-dashed border-slate-200 rounded-2xl p-8 flex flex-col items-center justify-center text-center hover:border-fuchsia-500 hover:bg-fuchsia-50/30 transition-all cursor-pointer group bg-slate-50/30 overflow-hidden"
                                        >
                                            {formData.imageUrl ? (
                                                <>
                                                    <img src={formData.imageUrl} alt="Cover" className="absolute inset-0 w-full h-full object-cover" />
                                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                        <p className="text-white font-bold">Click to change</p>
                                                    </div>
                                                </>
                                            ) : (
                                                <>
                                                    <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-4 shadow-sm group-hover:scale-110 transition-transform text-fuchsia-500 border border-slate-200">
                                                        <ImageIcon size={28} />
                                                    </div>
                                                    <p className="text-sm font-bold text-slate-900 mb-1">Click to upload or drag and drop</p>
                                                    <p className="text-xs text-slate-500 mb-4">SVG, PNG, JPG (max. 1200x600px)</p>
                                                </>
                                            )}
                                        </div>
                                        <input
                                            type="file"
                                            id="fileInput"
                                            className="hidden"
                                            accept="image/*"
                                            onChange={async (e) => {
                                                const file = e.target.files[0];
                                                if (!file) return;

                                                const uploadData = new FormData();
                                                uploadData.append('file', file);

                                                try {
                                                    const res = await fetch('/api/v1/upload', {
                                                        method: 'POST',
                                                        body: uploadData
                                                    });
                                                    if (!res.ok) throw new Error("Upload failed");
                                                    const data = await res.json();
                                                    handleChange({ target: { name: 'imageUrl', value: data.url } });
                                                } catch (err) {
                                                    alert("Failed to upload image");
                                                    console.error(err);
                                                }
                                            }}
                                        />
                                    </div>

                                    <input
                                        name="imageUrl"
                                        value={formData.imageUrl}
                                        onChange={handleChange}
                                        placeholder="Or paste direct image URL here..."
                                        className="mt-3 w-full px-4 py-2 text-sm bg-transparent border-b border-slate-200 focus:border-fuchsia-500 focus:outline-none transition-colors text-slate-500 text-center placeholder:text-slate-400"
                                    />
                                </div>
                            </div>

                            {/* SECTION 2: DATE & LOCATION */}
                            <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow hover:shadow-fuchsia-500/5">
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="w-10 h-10 rounded-2xl bg-fuchsia-50 text-fuchsia-600 flex items-center justify-center font-bold text-lg shadow-sm border border-fuchsia-100">2</div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-900">Date & Location</h3>
                                        <p className="text-sm text-slate-500">When and where is this happening?</p>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-8 mb-8">
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase tracking-wider">
                                            <Calendar size={14} /> Start
                                        </div>
                                        <div className="flex gap-3">
                                            <input type="date" name="startDate" value={formData.startDate} onChange={handleChange} className="flex-1 px-4 py-3 rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:ring-4 focus:ring-fuchsia-500/10 focus:border-fuchsia-500 outline-none transition-all font-medium text-slate-900" />
                                            <input type="time" name="startTime" value={formData.startTime} onChange={handleChange} className="w-32 px-4 py-3 rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:ring-4 focus:ring-fuchsia-500/10 focus:border-fuchsia-500 outline-none transition-all font-medium text-slate-900" />
                                        </div>
                                    </div>
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase tracking-wider">
                                            <Calendar size={14} /> End
                                        </div>
                                        <div className="flex gap-3">
                                            <input type="date" name="endDate" value={formData.endDate} onChange={handleChange} className="flex-1 px-4 py-3 rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:ring-4 focus:ring-fuchsia-500/10 focus:border-fuchsia-500 outline-none transition-all font-medium text-slate-900" />
                                            <input type="time" name="endTime" value={formData.endTime} onChange={handleChange} className="w-32 px-4 py-3 rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:ring-4 focus:ring-fuchsia-500/10 focus:border-fuchsia-500 outline-none transition-all font-medium text-slate-900" />
                                        </div>
                                    </div>

                                    <div className="mt-4 flex items-center gap-4 p-4 rounded-xl bg-slate-50/50 border border-slate-200 hover:border-slate-300 transition-colors">
                                        <Clock size={16} className="text-slate-400" />
                                        <div className="flex-1">
                                            <label className="text-[10px] font-bold uppercase text-slate-500 block tracking-wider mb-1">Time Zone</label>
                                            <select
                                                name="timezone"
                                                value={formData.timezone}
                                                onChange={handleChange}
                                                className="w-full bg-transparent font-bold text-slate-900 text-sm focus:outline-none"
                                            >
                                                <option value="Asia/Kolkata">India Standard Time (IST)</option>
                                                <option value="UTC">Universal Coordinated Time (UTC)</option>
                                                <option value="America/New_York">Eastern Time (ET)</option>
                                                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                                                <option value="Europe/London">British Summer Time (BST)</option>
                                            </select>
                                        </div>
                                        <div className="text-xs text-slate-600 font-medium bg-white px-2 py-1 rounded border border-slate-200">
                                            {new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <label className="block text-sm font-bold text-slate-500 uppercase tracking-wider text-[11px]">Location Type</label>
                                    <div className="flex gap-4">
                                        <button
                                            onClick={() => setFormData(p => ({ ...p, mode: 'offline' }))}
                                            className={`flex - 1 py - 4 px - 6 rounded - 2xl border - 2 flex items - center justify - center gap - 3 transition - all ${formData.mode === 'offline'
                                                ? 'border-fuchsia-500 bg-fuchsia-50/50 text-fuchsia-600 shadow-sm'
                                                : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'
                                                } `}
                                        >
                                            <div className={`w - 8 h - 8 rounded - full flex items - center justify - center ${formData.mode === 'offline' ? 'bg-fuchsia-500 text-white' : 'bg-slate-100 text-slate-400'} `}>
                                                <MapPin size={16} />
                                            </div>
                                            <span className="font-bold">In Person</span>
                                        </button>
                                        <button
                                            onClick={() => setFormData(p => ({ ...p, mode: 'online' }))}
                                            className={`flex - 1 py - 4 px - 6 rounded - 2xl border - 2 flex items - center justify - center gap - 3 transition - all ${formData.mode === 'online'
                                                ? 'border-fuchsia-500 bg-fuchsia-50/50 text-fuchsia-600 shadow-sm'
                                                : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'
                                                } `}
                                        >
                                            <div className={`w - 8 h - 8 rounded - full flex items - center justify - center ${formData.mode === 'online' ? 'bg-fuchsia-500 text-white' : 'bg-slate-100 text-slate-400'} `}>
                                                <Globe size={16} />
                                            </div>
                                            <span className="font-bold">Virtual Event</span>
                                        </button>
                                    </div>

                                    {formData.mode === 'offline' && (
                                        <div className="relative animate-in fade-in slide-in-from-top-2">
                                            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                                            <input
                                                name="location"
                                                value={formData.location}
                                                onChange={handleChange}
                                                placeholder="Search for a venue or enter full address..."
                                                className="w-full pl-12 pr-4 py-4 rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:outline-none focus:ring-4 focus:ring-fuchsia-500/10 focus:border-fuchsia-500 transition-all font-medium text-slate-900 placeholder:text-slate-500"
                                            />
                                        </div>
                                    )}

                                    {formData.mode === 'online' && (
                                        <div className="space-y-4 animate-in fade-in slide-in-from-top-2">
                                            <div className="relative">
                                                <Globe className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                                                <input
                                                    name="meetingLink"
                                                    value={formData.meetingLink}
                                                    onChange={handleChange}
                                                    placeholder="Meeting Link (Zoom, Meet, Teams...)"
                                                    className="w-full pl-12 pr-4 py-4 rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:outline-none focus:ring-4 focus:ring-fuchsia-500/10 focus:border-fuchsia-500 transition-all font-medium text-slate-900 placeholder:text-slate-500"
                                                />
                                            </div>
                                            <label className="flex items-center space-x-3 cursor-pointer p-1">
                                                <div className={`w - 5 h - 5 rounded border flex items - center justify - center transition - colors ${formData.meetingLinkPrivate ? 'bg-fuchsia-500 border-fuchsia-500' : 'border-slate-300'} `}>
                                                    {formData.meetingLinkPrivate && <Check size={12} className="text-white" />}
                                                </div>
                                                <input type="checkbox" checked={formData.meetingLinkPrivate} onChange={e => setFormData(p => ({ ...p, meetingLinkPrivate: e.target.checked }))} className="hidden" />
                                                <span className="text-sm text-slate-500 font-medium">Only show link to registered attendees</span>
                                            </label>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* SECTION 3: CONTENT (AGENDA & SPEAKERS) */}
                            <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow hover:shadow-fuchsia-500/5">
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="w-10 h-10 rounded-2xl bg-fuchsia-50 text-fuchsia-600 flex items-center justify-center font-bold text-lg shadow-sm border border-fuchsia-100">3</div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-900">Event Content</h3>
                                        <p className="text-sm text-slate-500">Enrich your event page with agenda and speakers.</p>
                                    </div>
                                </div>

                                <div className="space-y-10">
                                    {/* AGENDA */}
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-end">
                                            <label className="text-[11px] font-bold uppercase text-slate-500 block tracking-wider">Agenda (Optional)</label>
                                        </div>

                                        <div className="space-y-4">
                                            {formData.agendaItems.map((item, index) => (
                                                <div key={item.id} className="group relative bg-slate-50/50 border border-slate-200 rounded-2xl p-4 transition-all hover:border-fuchsia-200 hover:shadow-fuchsia-500/5">
                                                    <div className="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <button
                                                            onClick={() => removeAgendaItem(item.id)}
                                                            className="p-2 bg-white text-red-500 rounded-lg shadow-sm border border-slate-200 hover:bg-red-50"
                                                        >
                                                            <Trash2 size={16} />
                                                        </button>
                                                    </div>

                                                    <div className="flex flex-col md:flex-row gap-4 items-start">
                                                        <div className="flex items-center gap-2 bg-white p-2 rounded-xl border border-slate-200 shadow-sm shrink-0">
                                                            <div className="space-y-1">
                                                                <span className="text-[10px] items-center text-slate-400 font-bold px-2">TIME</span>
                                                                <div className="flex items-center gap-2">
                                                                    <input
                                                                        type="time"
                                                                        value={item.startTime}
                                                                        onChange={(e) => updateAgendaItem(item.id, 'startTime', e.target.value)}
                                                                        className="bg-transparent text-sm font-bold text-slate-900 focus:outline-none w-24 px-2"
                                                                    />
                                                                    <span className="text-slate-400">-</span>
                                                                    <input
                                                                        type="time"
                                                                        value={item.endTime}
                                                                        onChange={(e) => updateAgendaItem(item.id, 'endTime', e.target.value)}
                                                                        className="bg-transparent text-sm font-bold text-slate-900 focus:outline-none w-24 px-2"
                                                                    />
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div className="flex-1 w-full space-y-2">
                                                            <input
                                                                placeholder="e.g. Opening Keynote"
                                                                value={item.title}
                                                                onChange={(e) => updateAgendaItem(item.id, 'title', e.target.value)}
                                                                className="w-full bg-transparent text-lg font-bold text-slate-900 placeholder:text-slate-400 focus:outline-none focus:placeholder:text-slate-300"
                                                            />
                                                            <textarea
                                                                placeholder="Add a brief description of this session..."
                                                                value={item.description}
                                                                onChange={(e) => updateAgendaItem(item.id, 'description', e.target.value)}
                                                                rows={1}
                                                                className="w-full bg-transparent text-sm text-slate-500 placeholder:text-slate-400 focus:outline-none resize-none"
                                                                onInput={(e) => { e.target.style.height = 'auto'; e.target.style.height = e.target.scrollHeight + 'px' }}
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}

                                            <button
                                                onClick={addAgendaItem}
                                                className="w-full py-4 border-2 border-dashed border-slate-200 rounded-2xl flex items-center justify-center gap-2 text-slate-400 hover:text-fuchsia-600 hover:border-fuchsia-200 hover:bg-fuchsia-50/30 transition-all group"
                                            >
                                                <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center group-hover:bg-fuchsia-500 group-hover:text-white transition-colors">
                                                    <Plus size={16} />
                                                </div>
                                                <span className="font-bold text-sm">Add Session</span>
                                            </button>
                                        </div>
                                    </div>

                                    <div className="h-px bg-slate-200"></div>

                                    {/* SPEAKERS */}
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-end">
                                            <label className="text-[11px] font-bold uppercase text-slate-500 block tracking-wider">Speakers (Optional)</label>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {formData.speakers.map((item) => (
                                                <div key={item.id} className="relative group bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-lg hover:shadow-fuchsia-500/5 hover:border-fuchsia-200 transition-all">
                                                    <button
                                                        onClick={() => removeSpeaker(item.id)}
                                                        className="absolute top-2 right-2 p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                                                    >
                                                        <Trash2 size={14} />
                                                    </button>

                                                    <div className="flex items-start gap-4">
                                                        {/* Avatar Input */}
                                                        <div className="relative shrink-0">
                                                            <div className="w-16 h-16 rounded-2xl overflow-hidden bg-slate-100 border-2 border-slate-200 shadow-sm group-hover:scale-105 transition-transform">
                                                                {item.imageUrl ? (
                                                                    <img src={item.imageUrl} alt="" className="w-full h-full object-cover" />
                                                                ) : (
                                                                    <div className="w-full h-full flex items-center justify-center text-slate-400">
                                                                        <User size={24} />
                                                                    </div>
                                                                )}
                                                            </div>
                                                            <input
                                                                className="absolute inset-0 opacity-0 cursor-pointer"
                                                                placeholder="Paste URL"
                                                                onChange={(e) => {
                                                                    // URL input logic here
                                                                }}
                                                            />
                                                        </div>

                                                        <div className="flex-1 min-w-0 space-y-2">
                                                            <input
                                                                placeholder="Speaker Name"
                                                                value={item.name}
                                                                onChange={(e) => updateSpeaker(item.id, 'name', e.target.value)}
                                                                className="w-full bg-transparent font-bold text-slate-900 placeholder:text-slate-400 focus:outline-none"
                                                            />
                                                            <div className="space-y-1">
                                                                <input
                                                                    placeholder="Job Title"
                                                                    value={item.role}
                                                                    onChange={(e) => updateSpeaker(item.id, 'role', e.target.value)}
                                                                    className="w-full bg-transparent text-xs font-semibold text-slate-500 placeholder:text-slate-400 focus:outline-none"
                                                                />
                                                                <input
                                                                    placeholder="Company"
                                                                    value={item.company}
                                                                    onChange={(e) => updateSpeaker(item.id, 'company', e.target.value)}
                                                                    className="w-full bg-transparent text-xs text-slate-400 placeholder:text-slate-400 focus:outline-none"
                                                                />
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div className="mt-4 pt-3 border-t border-slate-100 flex gap-2">
                                                        <div className="flex-1 bg-slate-50 rounded-lg px-2 py-1.5 flex items-center gap-2 focus-within:ring-2 focus-within:ring-fuchsia-500/20 focus-within:bg-white transition-all">
                                                            <Linkedin size={12} className="text-[#0077b5]" />
                                                            <input
                                                                placeholder="LinkedIn URL"
                                                                value={item.linkedIn}
                                                                onChange={(e) => updateSpeaker(item.id, 'linkedIn', e.target.value)}
                                                                className="w-full bg-transparent text-[10px] focus:outline-none text-slate-600 placeholder:text-slate-400"
                                                            />
                                                        </div>
                                                        <div className="flex-1 bg-slate-50 rounded-lg px-2 py-1.5 flex items-center gap-2 focus-within:ring-2 focus-within:ring-fuchsia-500/20 focus-within:bg-white transition-all">
                                                            <ImageIcon size={12} className="text-slate-400" />
                                                            <input
                                                                placeholder="Image URL"
                                                                value={item.imageUrl}
                                                                onChange={(e) => updateSpeaker(item.id, 'imageUrl', e.target.value)}
                                                                className="w-full bg-transparent text-[10px] focus:outline-none text-slate-600 placeholder:text-slate-400"
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}

                                            <button
                                                onClick={addSpeaker}
                                                className="h-full min-h-[160px] border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center gap-3 text-slate-400 hover:text-fuchsia-600 hover:border-fuchsia-200 hover:bg-fuchsia-50/30 transition-all group p-6"
                                            >
                                                <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center group-hover:bg-fuchsia-500 group-hover:text-white transition-colors">
                                                    <Plus size={20} />
                                                </div>
                                                <span className="font-bold text-sm">Add Speaker</span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* AUDIENCE */}
                            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-md transition-shadow hover:shadow-fuchsia-500/5">
                                <h3 className="font-bold text-slate-900 mb-6 text-lg">Targeting</h3>
                                <div className="space-y-6">
                                    <div>
                                        <label className="text-[11px] font-bold uppercase text-slate-500 mb-2 block tracking-wider">Target Audience</label>
                                        <div className="relative">
                                            <Users size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                                            <select
                                                name="audience"
                                                value={formData.audience}
                                                onChange={handleChange}
                                                className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 bg-slate-50/50 appearance-none focus:outline-none focus:border-fuchsia-500 focus:bg-white transition-all font-medium text-sm text-slate-900"
                                            >
                                                <option>General Public</option>
                                                <option>Developers</option>
                                                <option>Founders</option>
                                                <option>Students</option>
                                            </select>
                                            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">▼</div>
                                        </div>
                                    </div>

                                    <div>
                                        <label className="text-[11px] font-bold uppercase text-slate-500 mb-2 block tracking-wider">Category</label>
                                        <div className="grid grid-cols-2 gap-2">
                                            {["Conference", "Workshop", "Networking", "Seminar"].map(cat => (
                                                <button
                                                    key={cat}
                                                    onClick={() => setFormData(p => ({ ...p, category: cat }))}
                                                    className={`px - 3 py - 2 rounded - lg text - xs font - bold border transition - all ${formData.category === cat
                                                        ? 'bg-fuchsia-500 text-white border-fuchsia-500'
                                                        : 'bg-slate-50 border-slate-200 text-slate-500 hover:border-slate-300'
                                                        } `}
                                                >
                                                    {cat}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <label className="text-[11px] font-bold uppercase text-slate-500 mb-2 block tracking-wider">Tags</label>
                                        <div className="flex flex-wrap gap-2 mb-3 min-h-[40px] p-2 rounded-xl bg-slate-50/50 border border-slate-200/50">
                                            {formData.tags.length === 0 && <span className="text-xs text-slate-400 p-1">No tags added</span>}
                                            {formData.tags.map(tag => (
                                                <span key={tag} className="px-3 py-1 bg-white text-fuchsia-600 text-xs font-bold rounded-lg border border-slate-200 shadow-sm flex items-center gap-2">
                                                    {tag} <button onClick={() => removeTag(tag)} className="hover:text-red-500 transition-colors">×</button>
                                                </span>
                                            ))}
                                        </div>
                                        <div className="relative">
                                            <Tag size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                                            <input
                                                placeholder="Add relevant tags..."
                                                onKeyDown={handleTagAdd}
                                                className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 bg-slate-50/50 text-sm focus:outline-none focus:border-fuchsia-500 focus:bg-white transition-all text-slate-900 placeholder:text-slate-500"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* TICKETING */}
                            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-md transition-shadow hover:shadow-fuchsia-500/5">
                                <h3 className="font-bold text-slate-900 mb-6 text-lg">Ticketing</h3>
                                <TicketManager
                                    tickets={formData.tickets}
                                    onChange={(newTickets) => setFormData(p => ({ ...p, tickets: newTickets }))}
                                />
                            </div>

                        </div>

                        {/* RIGHT COLUMN - PREVIEW (40%) */}
                        <div className="col-span-12 lg:col-span-5 space-y-8 relative">

                            {/* LIVE PREVIEW CARD */}
                            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm sticky top-8">
                                <h3 className="font-bold text-slate-900 mb-4 text-xs uppercase tracking-wider">Live Preview</h3>
                                <div className="border border-slate-200 rounded-2xl overflow-hidden bg-slate-50 shadow-sm">
                                    <div className="h-32 bg-slate-100 relative">
                                        {formData.imageUrl ? (
                                            <img src={formData.imageUrl} className="w-full h-full object-cover" alt="Preview" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-slate-300">
                                                <ImageIcon size={32} />
                                            </div>
                                        )}
                                        <div className="absolute top-3 right-3 bg-white/90 px-2 py-1 rounded-lg text-xs font-bold shadow-sm backdrop-blur-sm text-fuchsia-600 border border-fuchsia-100">
                                            {formData.isFree ? 'Free' : `₹${formData.ticketPrice}`}
                                        </div>
                                    </div>
                                    <div className="p-4">
                                        <div className="text-xs font-bold text-fuchsia-600 mb-1 uppercase tracking-wide">{formData.startDate || 'Date'} • {formData.category}</div>
                                        <h4 className="font-bold text-slate-900 mb-2 line-clamp-2">{formData.title || 'Event Title'}</h4>
                                        <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
                                            {formData.mode === 'online' ? <Globe size={12} /> : <MapPin size={12} />}
                                            <span className="truncate">{formData.mode === 'online' ? 'Online Event' : (formData.location || 'Location')}</span>
                                        </div>
                                        <div className="flex items-center justify-between border-t border-slate-100 pt-3 mt-3">
                                            <div className="flex -space-x-2">
                                                {[1, 2, 3].map(i => (
                                                    <div key={i} className="w-6 h-6 rounded-full bg-slate-200 border-2 border-white" />
                                                ))}
                                            </div>
                                            <span className="text-xs font-bold text-fuchsia-600 bg-fuchsia-50 px-3 py-1.5 rounded-lg border border-fuchsia-100">Register</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>


                {/* ACTION BUTTONS (Floating Dock) */}
                < div className="fixed bottom-6 lg:left-[calc(16rem+50%)] lg:-translate-x-1/2 lg:w-[calc(100%-18rem)] max-w-3xl w-[90%] left-1/2 -translate-x-1/2 z-40" >
                    <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800/50 p-4 rounded-2xl shadow-2xl flex items-center justify-between ring-1 ring-slate-900/5">
                        {/* Auto-save Indicator */}
                        <div className="flex items-center gap-3 pl-2">
                            <div className="relative">
                                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
                                <div className="absolute inset-0 bg-emerald-500 rounded-full animate-ping opacity-20"></div>
                            </div>
                            <span className="text-xs font-semibold text-slate-400">
                                Auto-saved <span className="text-slate-200">Just now</span>
                            </span>
                        </div>

                        {/* Button Group */}
                        <div className="flex items-center gap-3">
                            <button className="px-5 py-2.5 rounded-xl font-bold text-slate-400 hover:bg-slate-800/50 hover:text-white transition-all text-xs uppercase tracking-wider">
                                Draft
                            </button>
                            <button className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-slate-200 bg-slate-800/50 hover:bg-slate-700/50 transition-all text-xs uppercase tracking-wider">
                                <Eye size={16} /> Preview
                            </button>
                            <button
                                onClick={handleSubmit}
                                disabled={loading}
                                className="px-8 py-3 rounded-xl bg-cyan-500 text-slate-900 font-bold shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all text-sm flex items-center gap-2"
                            >
                                {loading ? 'Publishing...' : <>Publish Now <Check size={18} strokeWidth={3} /></>}
                            </button>
                        </div>
                    </div>
                </div >
                {/* SUCCESS MODAL */}
                {
                    showSuccessModal && (
                        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
                            <div className="bg-slate-900 rounded-3xl p-8 max-w-sm w-full shadow-2xl scale-100 animate-in zoom-in-95 duration-200 text-center border border-slate-800">
                                <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6 text-white shadow-lg shadow-green-500/30">
                                    <Check size={32} strokeWidth={3} />
                                </div>
                                <h2 className="text-2xl font-black text-white mb-2">Event Published! 🎉</h2>
                                <p className="text-slate-500 mb-8 font-medium">Your event is now live and ready to be shared with the world.</p>

                                <div className="space-y-3">
                                    <button
                                        onClick={() => {
                                            navigator.clipboard.writeText(`https://infinitebz.com/events/${createdEventId}`);
                                            alert("Link copied!");
                                        }}
                                        className="w-full py-3.5 rounded-xl border-2 border-slate-700 bg-slate-800 font-bold text-white hover:bg-slate-700 transition-colors flex items-center justify-center gap-2"
                                    >
                                        <Globe size={18} /> Copy Event Link
                                    </button >
                                    <button
                                        onClick={() => onNavigate('dashboard')}
                                        className="w-full py-3.5 rounded-xl bg-cyan-500 text-slate-900 font-bold hover:bg-cyan-600 transition-all shadow-lg shadow-cyan-500/25"
                                    >
                                        Go to Dashboard
                                    </button>
                                </div >
                            </div >
                        </div >
                    )
                }
            </main >
        </div >
    );
}

function ToolbarButton({ icon, label }) {
    return (
        <button className="p-2 rounded-lg hover:bg-slate-800 text-slate-500 transition-colors">
            {icon || label}
        </button>
    )
}
