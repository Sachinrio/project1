import React, { useRef, useState } from 'react';

export const MagneticButton = ({
    children,
    className = "",
    strength = 30,
    onClick
}) => {
    const ref = useRef(null);
    const [position, setPosition] = useState({ x: 0, y: 0 });

    const handleMouseMove = (e) => {
        if (!ref.current) return;

        const { clientX, clientY } = e;
        const { left, top, width, height } = ref.current.getBoundingClientRect();

        const x = clientX - (left + width / 2);
        const y = clientY - (top + height / 2);

        setPosition({ x: x / strength, y: y / strength });
    };

    const handleMouseLeave = () => {
        setPosition({ x: 0, y: 0 });
    };

    return (
        <div
            className="relative inline-block"
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
        >
            <div
                ref={ref}
                onClick={onClick}
                className={`transition-transform duration-200 ease-out ${className}`}
                style={{
                    transform: `translate(${position.x}px, ${position.y}px)`
                }}
            >
                {children}
            </div>
        </div>
    );
};
