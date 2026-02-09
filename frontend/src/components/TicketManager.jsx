import { useState } from 'react';
import { Plus, Trash2, Ticket, DollarSign, Users, Sparkles, AlertCircle } from 'lucide-react';

export default function TicketManager({ tickets, onChange }) {
    // Local state for the "Add Ticket" form
    const [isAdding, setIsAdding] = useState(false);
    const [newTicket, setNewTicket] = useState({
        type: 'paid', // free, paid
        name: '',
        price: '',
        quantity: '',
        description: ''
    });

    const handleAddTicket = () => {
        if (!newTicket.name || !newTicket.quantity) return; // Simple validation

        // If free, force price to 0
        const ticketToAdd = {
            ...newTicket,
            price: newTicket.type === 'free' ? 0 : parseFloat(newTicket.price) || 0,
            quantity: parseInt(newTicket.quantity) || 0,
            id: Date.now() // Temp ID for frontend key
        };

        onChange([...tickets, ticketToAdd]);
        setNewTicket({ type: 'paid', name: '', price: '', quantity: '', description: '' }); // Reset
        setIsAdding(false);
    };

    const removeTicket = (id) => {
        onChange(tickets.filter(t => t.id !== id));
    };

    const totalCapacity = tickets.reduce((acc, t) => acc + (parseInt(t.quantity) || 0), 0);

    return (
        <div className="space-y-6">

            {/* Ticket List */}
            <div className="space-y-3">
                {tickets.map((ticket) => (
                    <div key={ticket.id} className="bg-slate-800/40 border border-slate-700 rounded-xl p-4 flex justify-between items-center group hover:border-slate-600 transition-all">
                        <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${ticket.type === 'free' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                                <Ticket size={18} />
                            </div>
                            <div>
                                <h4 className="font-bold text-white text-sm">{ticket.name}</h4>
                                <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                                    <span className="flex items-center gap-1">
                                        <Users size={12} /> {ticket.quantity} available
                                    </span>
                                    {ticket.description && (
                                        <span className="max-w-[150px] truncate border-l border-slate-700 pl-3">
                                            {ticket.description}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-6">
                            <div className="text-right">
                                <span className={`block font-bold ${ticket.type === 'free' ? 'text-indigo-400' : 'text-emerald-400'}`}>
                                    {ticket.type === 'free' ? 'Free' : `₹${ticket.price}`}
                                </span>
                                <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Price</span>
                            </div>
                            <button
                                onClick={() => removeTicket(ticket.id)}
                                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:bg-red-500/10 hover:text-red-400 transition-colors"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    </div>
                ))}

                {tickets.length === 0 && !isAdding && (
                    <div className="text-center py-8 border-2 border-dashed border-slate-700/50 rounded-xl bg-slate-900/30">
                        <Ticket className="mx-auto text-slate-600 mb-2" size={32} />
                        <p className="text-slate-400 text-sm">No tickets created yet.</p>
                        <button onClick={() => setIsAdding(true)} className="mt-3 text-primary-400 text-sm font-bold hover:underline">
                            Create your first ticket
                        </button>
                    </div>
                )}
            </div>

            {/* Total Capacity Summary */}
            {tickets.length > 0 && (
                <div className="flex justify-between items-center bg-slate-900 border border-slate-700 rounded-lg p-3 px-4">
                    <span className="text-slate-400 text-sm font-medium">Total Capacity</span>
                    <span className="text-white font-bold">{totalCapacity} Attendees</span>
                </div>
            )}

            {/* Add Ticket Form */}
            {isAdding ? (
                <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 animate-in fade-in slide-in-from-bottom-2 duration-200">
                    <h4 className="font-bold text-white mb-4 flex items-center gap-2">
                        <Plus size={16} className="text-primary-500" /> New Ticket Class
                    </h4>

                    <div className="space-y-4">
                        {/* Type Selection */}
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={() => setNewTicket(p => ({ ...p, type: 'paid' }))}
                                className={`py-2 px-3 rounded-lg border text-sm font-bold transition-all ${newTicket.type === 'paid' ? 'bg-emerald-500/10 border-emerald-500 text-emerald-400' : 'border-slate-700 text-slate-400 hover:bg-slate-700'}`}
                            >
                                Paid Ticket
                            </button>
                            <button
                                onClick={() => setNewTicket(p => ({ ...p, type: 'free' }))}
                                className={`py-2 px-3 rounded-lg border text-sm font-bold transition-all ${newTicket.type === 'free' ? 'bg-indigo-500/10 border-indigo-500 text-indigo-400' : 'border-slate-700 text-slate-400 hover:bg-slate-700'}`}
                            >
                                Free Ticket
                            </button>
                        </div>

                        {/* Name & Quantity */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-400 uppercase">Ticket Name</label>
                                <input
                                    value={newTicket.name}
                                    onChange={e => setNewTicket(p => ({ ...p, name: e.target.value }))}
                                    placeholder="e.g. General Admission"
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-primary-500 outline-none"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-400 uppercase">Quantity available</label>
                                <input
                                    type="number"
                                    value={newTicket.quantity}
                                    onChange={e => setNewTicket(p => ({ ...p, quantity: e.target.value }))}
                                    placeholder="e.g. 100"
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-primary-500 outline-none"
                                />
                            </div>
                        </div>

                        {/* Price (if paid) */}
                        {newTicket.type === 'paid' && (
                            <div className="space-y-1 animate-in fade-in duration-200">
                                <label className="text-xs font-bold text-slate-400 uppercase">Price per ticket</label>
                                <div className="relative">
                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">₹</span>
                                    <input
                                        type="number"
                                        value={newTicket.price}
                                        onChange={e => setNewTicket(p => ({ ...p, price: e.target.value }))}
                                        placeholder="0.00"
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-8 pr-3 py-2 text-white text-sm focus:border-emerald-500 outline-none"
                                    />
                                </div>
                            </div>
                        )}

                        <div className="flex gap-3 pt-2">
                            <button
                                onClick={handleAddTicket}
                                disabled={!newTicket.name || !newTicket.quantity}
                                className="flex-1 bg-primary-600 hover:bg-primary-500 text-white font-bold py-2 rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Save Ticket
                            </button>
                            <button
                                onClick={() => setIsAdding(false)}
                                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-lg text-sm transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            ) : (
                <button
                    onClick={() => setIsAdding(true)}
                    className="w-full py-3 rounded-xl border-2 border-dashed border-slate-700 hover:border-primary-500/50 hover:bg-slate-800/50 text-slate-400 hover:text-white transition-all flex items-center justify-center gap-2 font-bold text-sm group"
                >
                    <Plus size={18} className="group-hover:text-primary-500 transition-colors" /> Add Ticket Class
                </button>
            )}

        </div>
    );
}
