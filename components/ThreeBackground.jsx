import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Environment } from '@react-three/drei';
import * as THREE from 'three';

const Geometries = () => {
    // We'll create a few floating shapes
    return (
        <group>
            <Float speed={1.5} rotationIntensity={1} floatIntensity={2}>
                <mesh position={[-4, 2, -5]} rotation={[0, 0, 0]}>
                    <icosahedronGeometry args={[1, 0]} />
                    <meshStandardMaterial color="#6366f1" roughness={0.1} metalness={0.5} transparent opacity={0.6} />
                </mesh>
            </Float>

            <Float speed={2} rotationIntensity={1.5} floatIntensity={1.5}>
                <mesh position={[4, -1, -6]}>
                    <torusGeometry args={[0.8, 0.2, 16, 100]} />
                    <meshStandardMaterial color="#10b981" roughness={0.1} metalness={0.8} transparent opacity={0.5} />
                </mesh>
            </Float>

            <Float speed={1} rotationIntensity={0.5} floatIntensity={1}>
                <mesh position={[0, -3, -8]}>
                    <dodecahedronGeometry args={[1.2, 0]} />
                    <meshStandardMaterial color="#06b6d4" roughness={0.2} metalness={0.6} transparent opacity={0.4} />
                </mesh>
            </Float>
        </group>
    );
};

export const ThreeBackground = () => {
    return (
        <div className="absolute inset-0 z-0 pointer-events-none">
            <Canvas camera={{ position: [0, 0, 10], fov: 45 }} gl={{ alpha: true, antialias: true }} dpr={[1, 2]}>
                <ambientLight intensity={0.5} />
                <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
                <pointLight position={[-10, -10, -10]} intensity={1} color="white" />
                <Geometries />
                <Environment preset="city" />
            </Canvas>
        </div>
    );
};
