/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Background & Dark Shades (Matching #0B1221)
                slate: {
                    50: '#f8fafc',
                    100: '#f1f5f9',
                    200: '#e2e8f0',
                    300: '#cbd5e1',
                    400: '#94a3b8',
                    500: '#64748b',
                    600: '#475569',
                    700: '#334155', // Borders/Muted
                    800: '#1e293b', // Cards / Secondary BG
                    900: '#0B1221', // PRIMARY BACKGROUND (Exact Match)
                    950: '#020617',
                },
                // Primary Accent: Cyan/Teal (Matching reference image)
                primary: {
                    DEFAULT: '#22d3ee', // Cyan 400 (Main)
                    400: '#22d3ee',
                    500: '#06b6d4',
                    600: '#0891b2',
                    glow: 'rgba(34, 211, 238, 0.5)'
                },
                // Keeping existing keys to prevent breakage, mapped to new palette
                gold: {
                    400: '#22d3ee',
                    500: '#06b6d4',
                    600: '#0891b2',
                },
                sky: {
                    400: '#22d3ee',
                    500: '#06b6d4',
                    600: '#0891b2',
                }
            }
        },
    },
    plugins: [],
}
