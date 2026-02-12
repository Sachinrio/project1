import React from 'react';
import {
    LayoutDashboard,
    Calendar,
    Ticket,
    Bell,
    Settings,
    LogOut,
    Plus,
    X,
    Menu,
    Infinity
} from 'lucide-react';

export default function Sidebar({ activePage, onNavigate, onLogout, onCreateClick }) {
    const [isOpen, setIsOpen] = React.useState(false);

    const menuItems = [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'my-events', label: 'My Events', icon: Calendar },
        { id: 'my-registrations', label: 'My Registrations', icon: Ticket },
    ];

    const toggleSidebar = () => setIsOpen(!isOpen);

    return (
        <>
            {/* Mobile Menu Button - Only visible on small screens */}
            <button
                onClick={toggleSidebar}
                className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-slate-800 text-white rounded-lg shadow-lg hover:bg-slate-700 transition-colors"
            >
                {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Overlay for mobile */}
            {isOpen && (
                <div
                    className="lg:hidden fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar Container */}
            <aside className={`
                fixed top-0 left-0 h-screen w-64 bg-white border-r border-slate-200 flex flex-col z-40 transition-transform duration-300
                ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            `}>
                <div className="h-full flex flex-col">
                    {/* Logo Area */}
                    <div className="h-24 flex items-center px-8">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                                <Infinity size={24} />
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xl font-black text-slate-900 font-outfit tracking-tight leading-none">
                                    InfiniteBZ
                                </span>
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">
                                    CHENNAI EDITION
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Menu Label */}
                    <div className="px-8 mt-4 mb-2">
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Menu</span>
                    </div>

                    {/* Navigation Links */}
                    <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
                        {menuItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = activePage === item.id;
                            return (
                                <button
                                    key={item.id}
                                    onClick={() => {
                                        onNavigate(item.id);
                                        setIsOpen(false);
                                    }}
                                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${isActive
                                        ? 'bg-indigo-50 text-indigo-600 font-bold'
                                        : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
                                        }`}
                                >
                                    <Icon size={20} className={isActive ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600 transition-colors'} />
                                    <span className="text-sm">{item.label}</span>
                                </button>
                            );
                        })}
                    </nav>


                    {/* Create Event Button */}
                    <div className="px-4 mt-4">
                        <button
                            onClick={onCreateClick}
                            className="w-full group relative px-4 py-3 bg-indigo-600 rounded-xl font-bold text-white shadow-lg shadow-indigo-600/25 hover:bg-indigo-700 transition-all hover:scale-[1.02] active:scale-[0.98]"
                        >
                            <span className="flex items-center justify-center gap-2">
                                <Plus size={20} className="group-hover:rotate-90 transition-transform duration-300" />
                                Create Event
                            </span>
                        </button>
                    </div>

                    {/* System Label */}
                    <div className="px-8 mt-6 mb-2">
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">System</span>
                    </div>

                    {/* Settings Item */}
                    <div className="px-4 mb-auto">
                        <button
                            onClick={() => onNavigate('settings')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${activePage === 'settings'
                                ? 'bg-indigo-50 text-indigo-600 font-bold'
                                : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
                                }`}
                        >
                            <Settings size={20} className={activePage === 'settings' ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600 transition-colors'} />
                            <span className="text-sm">Settings</span>
                        </button>
                    </div>

                    {/* Sign Out - Absolute bottom style */}
                    <div className="p-4 mt-auto">
                        <button
                            onClick={onLogout}
                            className="w-full flex items-center gap-3 px-4 py-3 text-slate-500 hover:text-indigo-600 hover:bg-slate-50 rounded-xl transition-all group"
                        >
                            <LogOut size={20} className="group-hover:text-indigo-600 transition-colors" />
                            <span className="text-sm font-medium">Sign Out</span>
                        </button>
                    </div>
                </div>
            </aside >
        </>
    );
}
