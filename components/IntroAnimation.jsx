import React, { useEffect, useState } from 'react';

export const IntroAnimation = ({ onComplete }) => {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        // Start fading out after 4.5 seconds (leaving 0.5s for fade)
        const fadeTimer = setTimeout(() => {
            setIsVisible(false);
        }, 4500);

        // Call onComplete after total 5 seconds
        const completeTimer = setTimeout(() => {
            onComplete();
        }, 5000);

        return () => {
            clearTimeout(fadeTimer);
            clearTimeout(completeTimer);
        };
    }, [onComplete]);

    return (
        <div className={`fixed inset-0 z-50 flex items-center justify-center bg-white transition-opacity duration-500 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
            <div className="relative w-80 h-80 md:w-96 md:h-96">
                {/* The Image with Circular Reveal Animation */}
                <img
                    src="/hands-circle.png"
                    onError={(e) => {
                        e.currentTarget.src = "/hands-circle.svg";
                    }}
                    alt="Community Hands"
                    className="w-full h-full object-contain animate-clock-wipe"
                />
            </div>
            <style>{`
        @keyframes clockWipe {
          0% {
            mask-image: conic-gradient(black 0deg, transparent 0deg);
            -webkit-mask-image: conic-gradient(black 0deg, transparent 0deg);
          }
          100% {
            mask-image: conic-gradient(black 360deg, transparent 360deg);
            -webkit-mask-image: conic-gradient(black 360deg, transparent 360deg);
          }
        }
        .animate-clock-wipe {
          animation: clockWipe 4s linear forwards;
          /* Ensure the mask handles the reveal */
          mask-mode: alpha;
          -webkit-mask-repeat: no-repeat;
          mask-repeat: no-repeat;
        }
      `}</style>
        </div>
    );
};
