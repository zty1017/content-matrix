// @ts-nocheck
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, ContactShadows } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';
import { MatrixCube } from './MatrixCube';
import { useCubeStore } from '../../store/useCubeStore';

export const CubeScene: React.FC = () => {
  const { setSelectedFaceId, isReconstructing } = useCubeStore();

  const handlePointerMissed = () => {
    setSelectedFaceId(null);
  };

  return (
    <div className="absolute inset-0 z-10">
      <Canvas 
        camera={{ position: [0, 0, 8], fov: 45 }}
        onPointerMissed={handlePointerMissed}
        gl={{ antialias: true, alpha: true }}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.6} color="#ffffff" />
          <directionalLight position={[10, 10, 5]} intensity={1.5} color="#e0f2fe" />
          <directionalLight position={[-10, -10, -5]} intensity={0.5} color="#bae6fd" />
          
          <Environment preset="city" />

          <MatrixCube />

          <ContactShadows 
            position={[0, -2.5, 0]} 
            opacity={0.3} 
            scale={10} 
            blur={2.5} 
            far={4} 
            color="#0f172a"
          />

          <OrbitControls 
            enablePan={false}
            enableZoom={false}
            minPolarAngle={Math.PI / 4}
            maxPolarAngle={Math.PI - Math.PI / 4}
            makeDefault
          />
        </Suspense>
      </Canvas>

      {/* Cinematic Smoke & Blur Effect Overlay */}
      <AnimatePresence>
        {isReconstructing && (
          <motion.div
            initial={{ opacity: 0, backdropFilter: 'blur(0px) brightness(1)' }}
            animate={{ opacity: 1, backdropFilter: 'blur(24px) brightness(1.2)' }}
            exit={{ opacity: 0, backdropFilter: 'blur(0px) brightness(1)' }}
            transition={{ duration: 0.8, ease: 'easeInOut' }}
            className="absolute inset-0 z-50 flex items-center justify-center pointer-events-none"
            style={{
              background: 'radial-gradient(circle at center, rgba(255,255,255,0.85) 0%, rgba(224,242,254,0.5) 40%, transparent 100%)'
            }}
          >
            <motion.div 
               animate={{ scale: [0.95, 1.05, 0.95], opacity: [0.6, 1, 0.6] }} 
               transition={{ repeat: Infinity, duration: 1.5 }}
               className="text-blue-500 font-bold tracking-[0.5em] text-xl drop-shadow-md"
            >
              MATRIX RECONSTRUCTING...
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
