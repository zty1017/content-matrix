// @ts-nocheck
import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { RoundedBox, Html, useTexture } from '@react-three/drei';
import { motion } from 'framer-motion-3d';
import * as THREE from 'three';
import { Video, Star, Database, Brain, ShieldCheck, Archive, Play } from 'lucide-react';
import { useCubeStore } from '../../store/useCubeStore';
import { useAppStore } from '../../store/useAppStore';
import { FACE_ROTATIONS, DEFAULT_VIEW_ANGLE, NORMAL_TO_FACE } from './constants';
import type { CubeFaceId } from '../../types/api';

const IconMap: Record<string, React.FC<any>> = {
  'video-camera': Video,
  'star': Star,
  'database': Database,
  'brain': Brain,
  'shield-check': ShieldCheck,
  'archive': Archive,
};

const COVER_IMAGES: Record<string, string> = {
  'food_decision': '/assets/covers/food-chongqing.jpg',
  'workplace_skit': '/assets/covers/workplace-waijuan.jpg',
  'finance_knowledge': '/assets/covers/finance-freedom.jpg'
};

const CUBIE_SIZE = 0.96;
const CUBIE_OFFSET = 1.0;
const OVERLAY_SIZE = 380; 
const OVERLAY_DISTANCE = 0.51;

const faceColors: Record<string, string> = {
  cyan: '#cffafe',
  blue: '#dbeafe',
  violet: '#ede9fe',
  amber: '#fef3c7',
  red: '#fee2e2',
  neutral: '#f1f5f9',
};

const textColors: Record<string, string> = {
  cyan: 'text-cyan-900',
  blue: 'text-blue-900',
  violet: 'text-violet-900',
  amber: 'text-amber-900',
  red: 'text-red-900',
  neutral: 'text-slate-800',
};

const getFaceId = (x: number, y: number, z: number): CubeFaceId | null => {
  if (x === 0 && y === 0 && z === 1) return 'primary_card';
  if (x === 0 && y === 0 && z === -1) return 'snapshot';
  if (x === 1 && y === 0 && z === 0) return 'evidence';
  if (x === -1 && y === 0 && z === 0) return 'related_assets';
  if (x === 0 && y === 1 && z === 0) return 'source';
  if (x === 0 && y === -1 && z === 0) return 'inferences';
  return null;
};

const getFaceRotation = (faceId: CubeFaceId): [number, number, number] => {
  switch (faceId) {
    case 'primary_card': return [0, 0, 0];
    case 'snapshot': return [0, Math.PI, 0];
    case 'evidence': return [0, Math.PI / 2, 0];
    case 'related_assets': return [0, -Math.PI / 2, 0];
    case 'source': return [-Math.PI / 2, 0, 0];
    case 'inferences': return [Math.PI / 2, 0, 0];
    default: return [0, 0, 0];
  }
};

const SolidSticker = ({ faceId, position, rotation, currentCubeView }: any) => {
  const faceData = currentCubeView?.faces?.[faceId];
  const color = faceData ? faceColors[faceData.accent] || faceColors.neutral : faceColors.neutral;
  return (
    <mesh position={position} rotation={rotation}>
      <planeGeometry args={[CUBIE_SIZE * 0.96, CUBIE_SIZE * 0.96]} />
      <meshPhysicalMaterial color={color} roughness={0.3} metalness={0.1} depthWrite={true} />
    </mesh>
  );
};

const SourceSticker = ({ x, z, textureUrl }: { x: number, z: number, textureUrl: string }) => {
  const texture = useTexture(textureUrl);
  const clonedTexture = useMemo(() => {
    const t = texture.clone();
    t.repeat.set(1/3, 1/3);
    t.offset.set((x + 1) / 3, (1 - z) / 3);
    t.needsUpdate = true;
    return t;
  }, [texture, x, z]);

  return (
    <mesh position={[0, CUBIE_SIZE / 2 + 0.002, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[CUBIE_SIZE * 0.96, CUBIE_SIZE * 0.96]} />
      <meshPhysicalMaterial map={clonedTexture} color="#777777" roughness={0.3} metalness={0.1} depthWrite={true} />
    </mesh>
  );
};

const OverlayContent = ({ faceData, isSelected, isReconstructing }: any) => {
  const { currentDemoContext } = useAppStore();
  const coverUrl = COVER_IMAGES[currentDemoContext] || COVER_IMAGES['food_decision'];
  const FaceIcon = faceData ? IconMap[faceData.icon] || Star : Star;

  if (!faceData) return null;

  return (
    <div 
      className={`flex flex-col transition-all duration-500 
      ${faceData.id !== 'source' ? (textColors[faceData.accent] || textColors.neutral) : 'text-white'} 
      ${isSelected ? 'scale-105 opacity-100' : 'opacity-95 hover:scale-105'}`}
      style={{ 
        width: OVERLAY_SIZE, 
        height: OVERLAY_SIZE, 
        background: 'transparent',
        pointerEvents: 'none',
        opacity: isReconstructing ? 0 : 1
      }}
    >
      {faceData.id === 'source' ? (
         <div className="flex flex-col items-center justify-center p-8 h-full">
            <div className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/40 shadow-[0_0_30px_rgba(0,0,0,0.5)] cursor-pointer hover:bg-white/30 transition-colors">
               <Play size={32} className="ml-1 text-white" fill="currentColor" />
            </div>
            <h3 className="mt-6 text-2xl font-extrabold drop-shadow-lg leading-tight text-center max-w-[80%] bg-black/30 px-4 py-2 rounded-xl backdrop-blur-sm border border-white/10">{faceData.summaryItems[0]?.split('：')[1] || faceData.summaryItems[0] || '视频'}</h3>
         </div>
      ) : (
         <div className="relative w-full h-full flex flex-col p-6">
           <div className="absolute -bottom-2 -right-2 opacity-10 pointer-events-none">
              <FaceIcon size={180} />
           </div>
           
           <div className="flex items-center gap-4 mb-4 relative z-10">
             <div className="p-3 rounded-2xl bg-white/40 backdrop-blur-md shadow-sm border border-white/50 text-current">
                <FaceIcon size={32} />
             </div>
             <span className="text-3xl font-extrabold drop-shadow-sm tracking-wide line-clamp-2">{faceData.label}</span>
           </div>
           
           <div className="flex-1 flex flex-col justify-center gap-3 relative z-10 w-full">
             {faceData.summaryItems.map((item: string, i: number) => (
               <div key={i} className="px-4 py-3 rounded-xl bg-white/50 border border-white/60 text-lg font-bold text-current shadow-sm backdrop-blur-sm flex items-start gap-3">
                 <div className="w-2 h-2 rounded-full bg-current opacity-60 shrink-0 mt-1.5"></div>
                 <span className="leading-snug line-clamp-3">{item}</span>
               </div>
             ))}
           </div>
         </div>
      )}
    </div>
  );
};

export const MatrixCube: React.FC = () => {
  const { selectedFaceId, setSelectedFaceId, twistEvent, clearTwistEvent, currentCubeView, isReconstructing, cubieResetTrigger } = useCubeStore();
  const { currentDemoContext } = useAppStore();
  
  const mainGroupRef = useRef<THREE.Group>(null);
  const cubiesRef = useRef<THREE.Mesh[]>([]);

  const animState = useRef({
    isTwisting: false,
    axis: 'y' as 'x'|'y'|'z',
    targetAngle: 0,
    startTime: 0,
    duration: 600,
    activeCubies: [] as {
      mesh: THREE.Mesh;
      startPos: THREE.Vector3;
      startQuat: THREE.Quaternion;
    }[]
  });

  const initialPositions = useMemo(() => {
    const coords = [];
    for (let x = -1; x <= 1; x++) {
      for (let y = -1; y <= 1; y++) {
        for (let z = -1; z <= 1; z++) {
          coords.push({
            pos: new THREE.Vector3(x * CUBIE_OFFSET, y * CUBIE_OFFSET, z * CUBIE_OFFSET),
            x, y, z
          });
        }
      }
    }
    return coords;
  }, []);

  const glassMaterial = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: '#f8fafc', 
    metalness: 0.1, 
    roughness: 0.2, 
    transmission: 0, 
    thickness: 0,
    clearcoat: 1.0, 
    clearcoatRoughness: 0.1, 
    transparent: false, 
    opacity: 1.0,
    depthWrite: true,
  }), []);

  const coreMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#38bdf8', emissive: '#0ea5e9', emissiveIntensity: 0.6,
  }), []);

  useEffect(() => {
    if (twistEvent && !animState.current.isTwisting) {
      const { axis, layer, angle, duration } = twistEvent;
      const activeCubies: any[] = [];
      
      cubiesRef.current.forEach(mesh => {
        if (!mesh) return;
        const posValue = mesh.position[axis];
        if (Math.abs(posValue - (layer * CUBIE_OFFSET)) < 0.5) {
          activeCubies.push({
            mesh,
            startPos: mesh.position.clone(),
            startQuat: mesh.quaternion.clone()
          });
        }
      });

      animState.current = {
        isTwisting: true,
        axis,
        targetAngle: angle,
        startTime: performance.now(),
        duration: duration || 600,
        activeCubies
      };
    }
  }, [twistEvent]);

  useFrame((state, delta) => {
    if (animState.current.isTwisting) {
      const { axis, targetAngle, startTime, duration, activeCubies } = animState.current;
      const now = performance.now();
      
      let progress = (now - startTime) / duration;
      let finished = false;
      if (progress >= 1.0) {
        progress = 1.0;
        finished = true;
      }

      const ease = progress < 0.5 ? 2 * progress * progress : 1 - Math.pow(-2 * progress + 2, 2) / 2;
      const currentAngle = ease * targetAngle;

      const axisVec = new THREE.Vector3(
        axis === 'x' ? 1 : 0,
        axis === 'y' ? 1 : 0,
        axis === 'z' ? 1 : 0
      );
      const pivotQuat = new THREE.Quaternion().setFromAxisAngle(axisVec, currentAngle);

      activeCubies.forEach(({ mesh, startPos, startQuat }) => {
        const newPos = startPos.clone().applyQuaternion(pivotQuat);
        mesh.position.copy(newPos);
        
        const newQuat = pivotQuat.clone().multiply(startQuat);
        mesh.quaternion.copy(newQuat);

        if (finished) {
          mesh.position.x = Math.round(mesh.position.x / CUBIE_OFFSET) * CUBIE_OFFSET;
          mesh.position.y = Math.round(mesh.position.y / CUBIE_OFFSET) * CUBIE_OFFSET;
          mesh.position.z = Math.round(mesh.position.z / CUBIE_OFFSET) * CUBIE_OFFSET;
          mesh.quaternion.normalize();
        }
      });

      if (finished) {
        animState.current.isTwisting = false;
        clearTwistEvent();
      }
    }

    if (!selectedFaceId && mainGroupRef.current && !twistEvent && !animState.current.isTwisting && !isReconstructing) {
      mainGroupRef.current.position.y = Math.sin(state.clock.elapsedTime * 1.5) * 0.05;
    } else if (mainGroupRef.current) {
      mainGroupRef.current.position.y = THREE.MathUtils.lerp(mainGroupRef.current.position.y, 0, 0.1);
    }
  });

  const handleCubieClick = (e: any) => {
    e.stopPropagation();
    if (twistEvent || animState.current.isTwisting) return; 
    if (e.face) {
      const normal = e.face.normal.clone().round();
      const faceId = NORMAL_TO_FACE[`${normal.x},${normal.y},${normal.z}`];
      if (faceId) setSelectedFaceId(faceId);
    }
  };

  const targetRotation = selectedFaceId ? FACE_ROTATIONS[selectedFaceId] : DEFAULT_VIEW_ANGLE;
  const coverUrl = COVER_IMAGES[currentDemoContext] || COVER_IMAGES['food_decision'];

  return (
    <motion.group
      ref={mainGroupRef as any}
      animate={{ rotateX: targetRotation[0], rotateY: targetRotation[1], rotateZ: targetRotation[2] }}
      transition={{ type: 'spring', stiffness: 60, damping: 15 }}
    >
      <group key={cubieResetTrigger}>
        {initialPositions.map((item, idx) => {
          const { pos, x, y, z } = item;
          const isCore = x === 0 && y === 0 && z === 0;
          const faceId = getFaceId(x, y, z);
          const faceData = faceId ? currentCubeView?.faces?.[faceId] : null;
          const isSelected = selectedFaceId === faceId;

          return (
            <group key={idx} ref={(el: any) => {
              if (el) {
                // Initialize position on creation
                el.position.copy(pos);
                cubiesRef.current[idx] = el;
              }
            }}>
              <RoundedBox
                args={[CUBIE_SIZE, CUBIE_SIZE, CUBIE_SIZE]}
                radius={0.05}
                smoothness={4}
                onClick={handleCubieClick}
                material={isCore ? coreMaterial : glassMaterial}
              >
                {z === 1 && <SolidSticker faceId="primary_card" position={[0, 0, CUBIE_SIZE / 2 + 0.002]} rotation={[0, 0, 0]} currentCubeView={currentCubeView} />}
                {z === -1 && <SolidSticker faceId="snapshot" position={[0, 0, -(CUBIE_SIZE / 2 + 0.002)]} rotation={[0, Math.PI, 0]} currentCubeView={currentCubeView} />}
                {x === 1 && <SolidSticker faceId="evidence" position={[CUBIE_SIZE / 2 + 0.002, 0, 0]} rotation={[0, Math.PI / 2, 0]} currentCubeView={currentCubeView} />}
                {x === -1 && <SolidSticker faceId="related_assets" position={[-(CUBIE_SIZE / 2 + 0.002), 0, 0]} rotation={[0, -Math.PI / 2, 0]} currentCubeView={currentCubeView} />}
                {y === -1 && <SolidSticker faceId="inferences" position={[0, -(CUBIE_SIZE / 2 + 0.002), 0]} rotation={[Math.PI / 2, 0, 0]} currentCubeView={currentCubeView} />}
                {y === 1 && <SourceSticker x={x} z={z} textureUrl={coverUrl} />}
              </RoundedBox>

              {faceId && faceData && (
                <Html
                  transform
                  position={[x * OVERLAY_DISTANCE, y * OVERLAY_DISTANCE, z * OVERLAY_DISTANCE]}
                  rotation={getFaceRotation(faceId)}
                  style={{ pointerEvents: 'none', backfaceVisibility: 'hidden' }}
                  distanceFactor={1.5}
                  zIndexRange={[100, 0]}
                  occlude={[mainGroupRef]}
                >
                  <OverlayContent faceData={faceData} isSelected={isSelected} isReconstructing={isReconstructing} />
                </Html>
              )}
            </group>
          );
        })}
      </group>
    </motion.group>
  );
};
