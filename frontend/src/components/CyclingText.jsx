import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const WORDS = ["Infinite", "Limitless", "Boundless", "Visionary"];

export const CyclingText = ({ className = "" }) => {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setIndex((prev) => (prev + 1) % WORDS.length);
        }, 3000); // Change every 3 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <span className={`inline-block relative min-w-[400px] text-center ${className}`}>
            <AnimatePresence mode="wait">
                <motion.span
                    key={index}
                    initial={{ y: 20, opacity: 0, filter: 'blur(10px)' }}
                    animate={{ y: 0, opacity: 1, filter: 'blur(0px)' }}
                    exit={{ y: -20, opacity: 0, filter: 'blur(10px)' }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className="absolute left-0 right-0 top-0 text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-blue-600 to-emerald-500 animate-gradient-text whitespace-nowrap"
                >
                    {WORDS[index]} Minded.
                </motion.span>
            </AnimatePresence>
            {/* Invisible placeholder to maintain width - use longest word */}
            <span className="opacity-0 whitespace-nowrap font-black">Visionary Minded.</span>
        </span>
    );
};
