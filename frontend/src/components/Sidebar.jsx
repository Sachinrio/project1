import { LayoutDashboard, ClipboardList, TrendingUp, Settings, LogOut, ScanLine, Plus, Infinity } from 'lucide-react';

export default function Sidebar({ activePage, onNavigate, onLogout, onCreateClick }) {
    return (
        <aside className="w-64 bg-slate-900 border-r border-white/20 flex flex-col fixed h-full z-20 hidden lg:flex text-white transition-all duration-300">
            <div className="p-6">
                <div className="flex items-center gap-3 font-bold text-xl text-white cursor-pointer" onClick={() => onNavigate('dashboard')}>
                    <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center shadow-lg shadow-white/10">
                        <Infinity className="text-primary-500" size={20} strokeWidth={3} />
                    </div>
                    <div>
                        InfiniteBZ
                        <span className="block text-[10px] font-normal text-white/70">Chennai Edition</span>
                    </div>
                </div>
            </div>

            <nav className="flex-1 px-4 space-y-1 mt-6">
                <NavItem
                    icon={<LayoutDashboard size={20} />}
                    label="Dashboard"
                    active={activePage === 'dashboard' || activePage === 'feed'}
                    onClick={() => onNavigate('dashboard')}
                />
                <NavItem
                    icon={<ClipboardList size={20} />}
                    label="My Events"
                    active={activePage === 'my-events'}
                    onClick={() => onNavigate('my-events')}
                />
                <NavItem
                    icon={<TrendingUp size={20} />}
                    label="My Registrations"
                    active={activePage === 'my-registrations'}
                    onClick={() => onNavigate('my-registrations')}
                />

                <NavItem
                    icon={<Settings size={20} />}
                    label="Settings"
                    active={activePage === 'settings'}
                    onClick={() => onNavigate('settings')}
                />
            </nav>

            <div className="p-4">
                <button
                    onClick={onCreateClick}
                    className="w-full py-3.5 bg-gradient-to-r from-primary-500 to-indigo-600 hover:from-primary-400 hover:to-indigo-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-primary-500/25 flex items-center justify-center gap-2 transform hover:scale-[1.02] active:scale-[0.98] group"
                >
                    <Plus size={18} className="text-white group-hover:rotate-90 transition-transform duration-300" />
                    <span className="text-xs uppercase tracking-wider font-bold">Create Event</span>
                </button>
                <button onClick={onLogout} className="flex items-center gap-3 px-4 py-3 w-full text-white/70 hover:text-white mt-4 transition-colors rounded-lg hover:bg-white/5">
                    <LogOut size={18} />
                    <span className="font-medium">Sign Out</span>
                </button>
            </div>
        </aside>
    );
}

function NavItem({ icon, label, active, onClick }) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-3 px-4 py-3 w-full rounded-xl transition-all mb-1 ${active
                ? 'bg-white/10 text-white font-bold border border-white/5'
                : 'text-white/70 hover:bg-white/5 hover:text-white'
                }`}
        >
            {icon}
            <span className="text-sm">{label}</span>
        </button>
    )
}
