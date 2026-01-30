import { useState } from 'react';
import { ArrowRight, CheckCircle2, Calendar, Database, MousePointer2, ChevronDown, ChevronUp, Clock, MapPin, Mail, Phone, MessageSquare, ExternalLink, Search, Infinity } from 'lucide-react';

export default function LandingPage({ onNavigate, onLogin, onSignup, events, user }) {
    const upcomingEvents = events.slice(0, 3);

    return (
        <div className="min-h-screen bg-slate-900 text-white font-sans selection:bg-primary-500/30">

            {/* 1. NAVBAR (Deep Contrast Header) */}
            <nav className="fixed w-full z-50 bg-slate-900/95 backdrop-blur-md border-b border-white/10 shadow-lg">
                <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center shadow-lg shadow-white/10">
                            <Infinity className="text-primary-500" size={20} strokeWidth={3} />
                        </div>
                        <span className="text-xl font-bold text-white tracking-tight">Infinite BZ</span>
                    </div>

                    <div className="hidden md:flex items-center gap-8 text-sm font-medium text-white/80">
                        <a href="#" className="hover:text-white transition-colors">Home</a>
                        <a href="#about" className="hover:text-white transition-colors">About</a>
                        <a href="#events" className="hover:text-white transition-colors">Events</a>
                        <a href="#contact" className="hover:text-white transition-colors">Contact</a>
                    </div>

                    {/* Login/Signup Buttons */}
                    <div className="flex items-center gap-4">
                        {!user && (
                            <button onClick={() => onLogin()} className="hidden md:block text-sm font-medium text-white hover:text-white/80 transition-colors">
                                Log In
                            </button>
                        )}

                        <button onClick={user ? onLogin : onSignup} className="hidden md:block text-sm font-medium text-white hover:text-white/80 transition-colors">
                            {user ? `Hi, ${user.full_name?.split(' ')[0] || 'User'} (Sign Out)` : 'Sign Up'}
                        </button>

                        {!user && (
                            <button
                                onClick={onSignup}
                                className="bg-primary-500 hover:bg-primary-600 text-slate-900 text-sm font-bold px-5 py-2.5 rounded-lg transition-all shadow-lg shadow-primary-500/20"
                            >
                                Get Started
                            </button>
                        )}
                    </div>
                </div>
            </nav>

            <section className="pt-40 pb-20 px-6">
                <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
                    <div className="max-w-2xl">
                        <span className="inline-block py-1 px-3 rounded-full bg-white/20 text-white text-xs font-bold uppercase tracking-wider mb-6 border border-white/20 shadow-sm">
                            Chennai's Event Aggregator
                        </span>
                        <h1 className="text-5xl lg:text-7xl font-bold text-white leading-[1.1] mb-6 tracking-tight drop-shadow-sm">
                            Chennai's <br />
                            Networking Scene. <br />
                            <span className="text-primary-400 drop-shadow-none">Unlocked.</span>
                        </h1>
                        <p className="text-lg text-white/80 mb-10 leading-relaxed max-w-lg">
                            Stop checking 15 different sites. Join the unified community platform. Discover, join, and grow your network with auto-updates for free events.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4">
                            <button
                                onClick={onNavigate}
                                className="bg-primary-500 hover:bg-primary-600 text-slate-900 font-bold px-8 py-4 rounded-xl transition-all shadow-lg shadow-primary-500/25 flex items-center justify-center gap-2"
                            >
                                Find Events Free
                                <ArrowRight size={20} />
                            </button>
                            <button className="px-8 py-4 rounded-xl font-semibold text-white border border-white/30 hover:bg-white/10 transition-all">
                                Request Feature
                            </button>
                        </div>


                    </div>

                    <div className="relative">
                        <div className="absolute -inset-1 bg-gradient-to-r from-primary-500 to-white rounded-2xl blur opacity-30"></div>
                        <div className="relative rounded-2xl overflow-hidden border border-white/20 shadow-2xl bg-white/10 backdrop-blur-sm">
                            <img
                                src="https://images.unsplash.com/photo-1544531586-fde5298cdd40?q=80&w=2070&auto=format&fit=crop"
                                alt="Conference Hall"
                                className="w-full object-cover opacity-90"
                            />

                            <div className="absolute bottom-6 left-6 right-6 bg-slate-900/90 backdrop-blur-xl p-4 rounded-xl border border-white/10 flex items-center justify-between">
                                <div>
                                    <div className="text-xs text-primary-400 font-bold mb-1">NEXT UP</div>
                                    <div className="text-white font-semibold">Tech Meetup @ IIT Madras</div>
                                </div>
                                <button onClick={onNavigate} className="px-4 py-2 bg-primary-500 rounded-lg text-xs font-bold text-slate-900 hover:bg-primary-400">JOIN</button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 3. STATS (Glassy Light) */}
            <section className="border-y border-white/10 bg-white/10 backdrop-blur-md py-12">
                <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-8 text-center md:text-left">
                    {[
                        { label: 'Platforms Aggregated', val: '15+', icon: Database },
                        { label: 'Events Listed Monthly', val: '500+', icon: Calendar },
                        { label: 'Fast Registration', val: '3 sec', icon: Clock },
                    ].map((stat, idx) => (
                        <div key={idx} className="flex items-center gap-4 justify-center md:justify-start">
                            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-white">
                                <stat.icon size={24} />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">{stat.val}</div>
                                <div className="text-sm text-white/60 uppercase tracking-widest font-semibold">{stat.label}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* 3.5 HOW IT WORKS (New Section) */}
            <section className="py-24 px-6 bg-[#0B1221]">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center max-w-2xl mx-auto mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">How It Works</h2>
                        <p className="text-white/60">Get started in 3 simple steps. No complicated signups.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-12 relative">
                        {/* Connecting Line (Desktop) */}
                        <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-0.5 bg-gradient-to-r from-red-500/0 via-primary-500/50 to-red-500/0 border-t border-dashed border-white/20"></div>

                        {[
                            { step: "01", title: "Choose Your City", desc: "Select Chennai (more coming soon) to see local tech events.", icon: MapPin },
                            { step: "02", title: "Browse Events", desc: "Filter by free, paid, startup, or networking categories.", icon: Search },
                            { step: "03", title: "Register & Attend", desc: "Click through to the official page and secure your spot.", icon: ExternalLink }
                        ].map((item, i) => (
                            <div key={i} className="relative flex flex-col items-center text-center">
                                <div className="w-24 h-24 rounded-2xl bg-[#1A2338] border border-white/10 flex items-center justify-center text-primary-500 mb-6 relative z-10 shadow-xl shadow-black/50 group hover:-translate-y-2 transition-transform duration-300">
                                    <item.icon size={32} />
                                    <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-primary-500 text-slate-900 font-bold flex items-center justify-center text-sm border-2 border-slate-900">
                                        {item.step}
                                    </div>
                                </div>
                                <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                                <p className="text-white/60 leading-relaxed max-w-xs">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* 4. WHY CHOOSE US (Glassy Light Continued) */}
            <section id="about" className="py-24 px-6 relative overflow-hidden bg-transparent">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center max-w-2xl mx-auto mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Why Choose Us?</h2>
                        <p className="text-white/80">We aggregate data from multiple sources so you don't have to search manually.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            { title: 'Unified Feed', desc: 'No more tab switching. View all Meetup, Eventbrite, and Luma events in one dashboard.', icon: Database },
                            { title: 'Curated Data', desc: 'We clean and verify data. No more broken links or outdated event times.', icon: CheckCircle2 },
                            { title: '1-Click Register', desc: 'Jump straight to the registration page. No login walls on our end.', icon: MousePointer2 },
                        ].map((item, i) => (
                            <div key={i} className="p-8 rounded-2xl bg-white/10 border border-white/10 hover:border-primary-500/30 hover:bg-white/15 transition-all group backdrop-blur-sm">
                                <div className="w-14 h-14 rounded-xl bg-white/10 flex items-center justify-center text-white mb-6 group-hover:bg-primary-500 group-hover:text-slate-900 transition-all">
                                    <item.icon size={28} />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                                <p className="text-white/70 leading-relaxed">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* 5. UPCOMING EVENTS (DYNAMIC) */}
            <section id="events" className="py-24 px-6 bg-slate-900/30">
                <div className="max-w-7xl mx-auto">
                    <div className="flex justify-between items-end mb-12">
                        <div>
                            <h2 className="text-3xl font-bold text-white mb-2">Upcoming in Chennai</h2>
                            <p className="text-slate-400">Don't miss out on these popular events.</p>
                        </div>
                        <button onClick={onNavigate} className="text-sky-400 font-semibold hover:text-sky-300 flex items-center gap-2">
                            View All Events <ArrowRight size={16} />
                        </button>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6">
                        {events.length > 0 ? [...events]
                            .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
                            .slice(0, 3)
                            .map(event => (
                                <div key={event.id} className="group bg-slate-900 rounded-xl overflow-hidden border border-white/5 hover:border-sky-500/50 hover:shadow-xl hover:shadow-sky-500/10 transition-all hover:-translate-y-1">
                                    <div className="h-48 bg-slate-800 relative overflow-hidden">
                                        {event.image_url ? (
                                            <img src={event.image_url} alt={event.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                                        ) : (
                                            <div className="flex items-center justify-center h-full text-slate-600 bg-slate-800">
                                                <Calendar size={32} opacity={0.2} />
                                            </div>
                                        )}
                                        <div className="absolute top-3 right-3 bg-slate-950/90 px-3 py-1 rounded-full text-xs font-bold text-sky-400 border border-sky-500/20 backdrop-blur-sm">
                                            {event.is_free ? 'FREE' : 'PAID'}
                                        </div>
                                    </div>

                                    <div className="p-5 flex-1 flex flex-col h-full">
                                        <h3 className="text-lg font-bold text-white mb-3 line-clamp-2 min-h-[3.5rem] leading-tight" title={event.title}>{event.title}</h3>

                                        <div className="space-y-3 text-sm text-slate-400 mb-6 flex-1">
                                            <div className="flex items-center gap-3">
                                                <div className="p-1.5 bg-slate-800 rounded-lg text-sky-500">
                                                    <Calendar size={14} />
                                                </div>
                                                <span className="font-medium text-slate-300">
                                                    {new Date(event.start_time).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <div className="p-1.5 bg-slate-800 rounded-lg text-sky-500">
                                                    <MapPin size={14} />
                                                </div>
                                                <span className="line-clamp-1">{event.venue_name}</span>
                                            </div>
                                        </div>

                                        <button onClick={() => window.open(event.url, '_blank')} className="w-full bg-slate-800 hover:bg-sky-600 hover:text-white text-slate-200 font-semibold py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 group-hover:shadow-lg">
                                            <span>Register Now</span>
                                            <ExternalLink size={16} />
                                        </button>
                                    </div>
                                </div>
                            )) : (
                            <div className="col-span-3 text-center py-12 text-slate-500 animate-pulse">Loading events...</div>
                        )}
                    </div>
                </div>
            </section>

            {/* 6. TESTIMONIALS */}
            <section className="py-24 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-white">Loved by Chennai's Tech Scene</h2>
                    </div>

                    <div className="grid md:grid-cols-2 gap-8">
                        {[
                            { quote: "Finally a unified list. I used to check 3 different sites every Friday. This saved me so much time.", author: "Arjun K.", role: "Product Manager" },
                            { quote: "The curated data is actually accurate. Finding free networking events properly categorized is a game changer.", author: "Priya S.", role: "Freelance Developer" }
                        ].map((t, i) => (
                            <div key={i} className="bg-slate-900 p-8 rounded-2xl border border-white/5 relative">
                                <div className="text-sky-500 text-4xl font-serif absolute top-6 left-6">"</div>
                                <p className="text-lg text-slate-300 italic mb-6 pl-6 relative z-10">{t.quote}</p>
                                <div className="flex items-center gap-4 pl-6">
                                    <div className="w-10 h-10 rounded-full bg-slate-700" />
                                    <div>
                                        <div className="text-white font-bold">{t.author}</div>
                                        <div className="text-xs text-slate-500">{t.role}</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* 7. FAQ */}
            <section className="py-24 px-6 bg-slate-900/30">
                <div className="max-w-3xl mx-auto">
                    <h2 className="text-3xl font-bold text-white text-center mb-12">Frequently Asked Questions</h2>
                    <div className="space-y-4">
                        {[
                            { q: "Is this platform really free?", a: "Yes! Use the aggregator for free. We might add premium features for organizers later." },
                            { q: "How often are events updated?", a: "We scrape new events daily at 8:00 AM, ensuring you have the latest info." },
                            { q: "Can I post my own event?", a: "Currently we only aggregate. A 'Submit Event' feature is coming soon." }
                        ].map((faq, i) => (
                            <details key={i} className="group bg-slate-900 rounded-xl overflow-hidden border border-white/5">
                                <summary className="flex items-center justify-between p-6 cursor-pointer font-semibold text-white hover:bg-white/5 transition-colors">
                                    {faq.q}
                                    <ChevronDown className="group-open:rotate-180 transition-transform text-slate-500" />
                                </summary>
                                <div className="px-6 pb-6 text-slate-400">
                                    {faq.a}
                                </div>
                            </details>
                        ))}
                    </div>
                </div>
            </section>

            {/* 8. FOOTER / CONTACT */}
            <footer id="contact" className="py-20 px-6 bg-[#050911] border-t border-white/5">
                <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16">
                    <div>
                        <h2 className="text-3xl font-bold text-white mb-6">Get in touch</h2>
                        <p className="text-slate-400 mb-8">Have questions? Want to feature your community? Drop us a line.</p>

                        <div className="space-y-6">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-sky-500"><Mail size={20} /></div>
                                <div>
                                    <div className="text-white font-semibold">Email Us</div>
                                    <div className="text-sm text-slate-500">hello@infinitebz.com</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-sky-500"><MessageSquare size={20} /></div>
                                <div>
                                    <div className="text-white font-semibold">Help Center</div>
                                    <div className="text-sm text-slate-500">Call support available 9-5</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-900 p-8 rounded-2xl border border-white/5">
                        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1">
                                    <label className="text-xs font-bold text-slate-400">FIRST NAME</label>
                                    <input type="text" className="w-full bg-[#0B1221] border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-sky-500 transition-colors" />
                                </div>
                                <div className="space-y-1">
                                    <label className="text-xs font-bold text-slate-400">LAST NAME</label>
                                    <input type="text" className="w-full bg-[#0B1221] border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-sky-500 transition-colors" />
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-400">EMAIL</label>
                                <input type="email" className="w-full bg-[#0B1221] border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-sky-500 transition-colors" />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-400">MESSAGE</label>
                                <textarea rows={4} className="w-full bg-[#0B1221] border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-sky-500 transition-colors"></textarea>
                            </div>
                            <button className="w-full bg-sky-500 hover:bg-sky-400 text-white font-bold py-4 rounded-lg transition-colors shadow-lg shadow-sky-500/20">
                                Send Message
                            </button>
                        </form>
                    </div>
                </div>

                <div className="border-t border-white/5 mt-20 pt-8 text-center text-sm text-slate-600">
                    © 2024 Infinite BZ. All rights reserved.
                </div>
            </footer>

            {/* CTA Bottom */}
            <section className="bg-sky-500 py-16 px-6 text-center">
                <h2 className="text-3xl font-bold text-white mb-4">Ready to expand your network?</h2>
                <p className="text-white/80 mb-8 max-w-xl mx-auto">Join 500+ professionals in Chennai and never miss an opportunity.</p>
                <div className="flex justify-center gap-4">
                    <button onClick={onSignup} className="bg-white text-sky-600 font-bold px-8 py-3 rounded-lg shadow-xl hover:bg-slate-100 transition-colors">Get Started Free</button>
                </div>
            </section>
        </div>
    )
}
