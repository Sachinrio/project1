import { useState } from 'react';
import { Sparkles, Calendar, Clock, AlertCircle, Wand2 } from 'lucide-react';

export default function Step2_AIMagic({ formData, updateFormData, onNext, onBack }) {
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState(null);

    // Calculate duration string for AI
    const getDuration = () => {
        if (!formData.startTime || !formData.endTime) return "2 hours";
        // Simple mock calculation or just assume 2 hours if complex
        // Ideally parse times and diff
        return "2 hours";
    };

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);

        try {
            const duration = getDuration();
            const payload = {
                title: formData.title,
                category: formData.category,
                duration: duration,
                start_time: formData.startTime || "10:00"
            };

            // Assuming Vite proxy or absolute URL. Using absolute for clarity based on existing code.
            const response = await fetch('/api/v1/ai/generate-event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Generation failed");
            }

            const data = await response.json();

            // TRANSFORM BACKEND DATA TO FORM FORMAT
            // Validating keys exist
            const updates = {};
            if (data.description) updates.description = data.description;
            if (data.imageUrl && !formData.imageUrl) updates.imageUrl = data.imageUrl; // Don't overwrite if user set one? Or overwrite? User implies they want AI.
            // Actually, let's overwrite for "Magic"
            if (data.imageUrl) updates.imageUrl = data.imageUrl;

            if (data.agenda) {
                // Map agenda items to include IDs
                updates.agendaItems = data.agenda.map((item, idx) => ({
                    id: Date.now() + idx,
                    startTime: item.startTime,
                    endTime: item.endTime,
                    title: item.title,
                    description: item.description
                }));
            }

            if (data.speakers) {
                updates.speakers = data.speakers.map((item, idx) => ({
                    id: Date.now() + idx + 100,
                    name: item.name,
                    role: item.role,
                    company: item.company,
                    imageUrl: "", // AI doesn't give speaker images usually, logic in backend might suggest urls but typically not
                    linkedIn: ""
                }));
            }

            if (data.tags) updates.tags = data.tags;

            updates.aiGenerated = true; // Flag for UI to maybe show "AI Generated" badge

            updateFormData(updates);
            onNext(); // Auto-advance to Agenda (Step 3)

        } catch (err) {
            console.error("AI Generation Error:", err);
            setError(err.message);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-right-8 duration-500">
            <div className="text-center space-y-4">
                <div className="w-20 h-20 mx-auto rounded-3xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/30 mb-6">
                    <Sparkles size={40} className="text-white animate-pulse" />
                </div>
                <h3 className="text-3xl font-bold text-white">AI Magic Build</h3>
                <p className="text-slate-400 max-w-lg mx-auto">
                    We can automatically generate a detailed agenda, speakers list, and description based on your title.
                </p>
            </div>

            <div className="max-w-xl mx-auto bg-white/5 border border-white/10 rounded-3xl p-8 space-y-6">

                {/* Context Card */}
                <div className="bg-slate-900/50 rounded-2xl p-4 border border-white/5 flex gap-4 items-center">
                    <div className="w-12 h-12 bg-indigo-500/20 rounded-full flex items-center justify-center text-indigo-400 shrink-0">
                        <Wand2 size={24} />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Generating Content For</p>
                        <h4 className="font-bold text-white text-lg">{formData.title || "Untitled Event"}</h4>
                        <div className="flex gap-3 text-xs text-slate-400 mt-1">
                            <span className="flex items-center gap-1"><Calendar size={12} /> {formData.startDate || "Date TBD"}</span>
                            <span className="flex items-center gap-1"><Clock size={12} /> {formData.startTime || "10:00"}</span>
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl flex items-center gap-3 text-sm">
                        <AlertCircle size={16} />
                        {error}
                    </div>
                )}

                <button
                    onClick={handleGenerate}
                    disabled={isGenerating || !formData.title}
                    className="w-full py-4 rounded-2xl font-bold text-white text-lg bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-[length:200%_auto] animate-gradient hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all flex items-center justify-center gap-3 shadow-xl shadow-indigo-600/20"
                >
                    {isGenerating ? (
                        <>Generating Magic <span className="animate-spin text-xl">✨</span></>
                    ) : (
                        <>Generate with AI <Sparkles size={20} className="animate-pulse" /></>
                    )}
                </button>

                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-white/10"></div>
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-[#1a1a1a] px-2 text-slate-500">Or skip for now</span>
                    </div>
                </div>

                <button
                    onClick={onNext}
                    disabled={isGenerating}
                    className="w-full py-3 rounded-xl border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 transition-all font-bold text-sm"
                >
                    Continue Manual Setup
                </button>

            </div>
        </div>
    );
}
