import { useState } from 'react';

function CityDropdown({ selected, onChange }) {
    const [isOpen, setIsOpen] = useState(false);
    const cities = ["All Cities", "Chennai", "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Kolkata", "Pune"];

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${selected !== "All Cities"
                    ? 'bg-sky-50 border-sky-200 text-sky-600'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
            >
                {selected === "All Cities" ? "City: All" : `City: ${selected}`}
                <span className="text-[10px] opacity-50">▼</span>
            </button>

            {isOpen && (
                <>
                    <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)}></div>
                    <div className="absolute top-full mt-2 left-0 w-48 bg-white border border-slate-200 rounded-lg shadow-xl z-20 py-1 max-h-60 overflow-y-auto">
                        {cities.map(city => (
                            <button
                                key={city}
                                onClick={() => {
                                    onChange(city);
                                    setIsOpen(false);
                                }}
                                className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-50 ${selected === city ? 'text-sky-600 font-bold bg-sky-50' : 'text-slate-600'}`}
                            >
                                {city}
                            </button>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
export default CityDropdown;
