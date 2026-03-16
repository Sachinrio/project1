import { Plus, Trash2, Clock, AlignLeft } from 'lucide-react';
import { motion, Reorder } from 'framer-motion';

export default function Step3_Agenda({ formData, updateFormData, onNext, onBack }) {

    const addSession = () => {
        const newItem = {
            id: Date.now(),
            startTime: "09:00",
            endTime: "10:00",
            title: "",
            description: ""
        };
        updateFormData({ agendaItems: [...formData.agendaItems, newItem] });
    };

    const removeSession = (id) => {
        updateFormData({ agendaItems: formData.agendaItems.filter(item => item.id !== id) });
    };

    const updateSession = (id, field, value) => {
        updateFormData({
            agendaItems: formData.agendaItems.map(item =>
                item.id === id ? { ...item, [field]: value } : item
            )
        });
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-right-8 duration-500">
            <div className="text-center space-y-2">
                <h3 className="text-3xl font-bold text-white">The Agenda</h3>
                <p className="text-slate-400">Plan out the schedule for your attendees.</p>
            </div>

            <div className="space-y-4">
                {formData.agendaItems.length === 0 && (
                    <div className="text-center p-8 border-2 border-dashed border-white/10 rounded-3xl text-slate-500">
                        <p>No sessions added yet.</p>
                        <button onClick={addSession} className="mt-4 text-indigo-400 font-bold hover:underline">Add your first session</button>
                    </div>
                )}

                <div className="space-y-4">
                    {formData.agendaItems.map((item, index) => (
                        <motion.div
                            key={item.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white/5 border border-white/10 rounded-2xl p-6 relative group hover:border-indigo-500/30 transition-all"
                        >
                            <button
                                onClick={() => removeSession(item.id)}
                                className="absolute top-4 right-4 p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                            >
                                <Trash2 size={16} />
                            </button>

                            <div className="flex flex-col md:flex-row gap-6 items-start">
                                {/* Time Input */}
                                <div className="flex items-center gap-2 bg-black/20 p-2 rounded-xl border border-white/5 shrink-0">
                                    <Clock size={16} className="text-slate-500 ml-2" />
                                    <input
                                        type="time"
                                        value={item.startTime}
                                        onChange={(e) => updateSession(item.id, 'startTime', e.target.value)}
                                        className="bg-transparent text-white font-mono text-sm focus:outline-none w-20 text-center"
                                    />
                                    <span className="text-slate-600">-</span>
                                    <input
                                        type="time"
                                        value={item.endTime}
                                        onChange={(e) => updateSession(item.id, 'endTime', e.target.value)}
                                        className="bg-transparent text-white font-mono text-sm focus:outline-none w-20 text-center"
                                    />
                                </div>

                                {/* Content Input */}
                                <div className="flex-1 w-full space-y-3">
                                    <input
                                        value={item.title}
                                        onChange={(e) => updateSession(item.id, 'title', e.target.value)}
                                        placeholder="Session Title (e.g. Opening Keynote)"
                                        className="w-full bg-transparent text-xl font-bold text-white placeholder:text-slate-600 focus:outline-none border-b border-transparent focus:border-indigo-500/50 pb-1 transition-all"
                                    />
                                    <div className="relative">
                                        <AlignLeft className="absolute top-1 left-0 text-slate-600" size={16} />
                                        <input
                                            value={item.description}
                                            onChange={(e) => updateSession(item.id, 'description', e.target.value)}
                                            placeholder="Brief description of what happen's in this session..."
                                            className="w-full bg-transparent pl-6 text-sm text-slate-400 placeholder:text-slate-700 focus:outline-none"
                                        />
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                <button
                    onClick={addSession}
                    className="w-full py-4 border-2 border-dashed border-white/10 rounded-2xl text-slate-500 hover:text-indigo-400 hover:border-indigo-500/30 hover:bg-indigo-500/5 transition-all flex items-center justify-center gap-2 font-bold"
                >
                    <Plus size={20} /> Add Session
                </button>
            </div>

            <div className="flex justify-between pt-8 border-t border-white/10">
                <button
                    onClick={onBack}
                    className="px-6 py-3 rounded-xl text-slate-400 hover:text-white font-bold transition-colors"
                >
                    Back
                </button>
                <button
                    onClick={onNext}
                    className="px-8 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-all shadow-lg shadow-indigo-600/20"
                >
                    Next Step
                </button>
            </div>
        </div>
    );
}
