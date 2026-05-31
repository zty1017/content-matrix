import { useCubeStore } from '../store/useCubeStore';
import { useCabinetStore } from '../store/useCabinetStore';
import { useAppStore } from '../store/useAppStore';

const delay = (ms: number) => {
  const { animationSpeed } = useAppStore.getState();
  if (animationSpeed === 'skip') return Promise.resolve();
  const actualMs = animationSpeed === 'fast' ? ms / 2 : ms;
  return new Promise(res => setTimeout(res, actualMs));
};

const getTwistDuration = (duration: number) => {
  const { animationSpeed } = useAppStore.getState();
  if (animationSpeed === 'skip') return 10; // Must be >0 to let useFrame process it at least once, but very fast
  return animationSpeed === 'fast' ? duration / 2 : duration;
};

export const runOneClickDemoSequence = async () => {
  const cubeStore = useCubeStore.getState();
  const cabinetStore = useCabinetStore.getState();

  cubeStore.setIsAnimating(true);
  cubeStore.setSelectedFaceId(null);
  cubeStore.setInteractionState('animating');
  
  cubeStore.setNarrativeStage('source_resolution');
  cubeStore.updateCubePhase('source_resolution');
  
  // Start cinematic effect earlier to cover the whole process
  cubeStore.setReconstructing(true);
  
  await delay(800);
  
  await cubeStore.triggerTwist({ axis: 'y', layer: 1, angle: Math.PI / 2, duration: getTwistDuration(300) });
  await cubeStore.triggerTwist({ axis: 'x', layer: 1, angle: -Math.PI / 2, duration: getTwistDuration(300) });
  await cubeStore.triggerTwist({ axis: 'z', layer: 1, angle: Math.PI / 2, duration: getTwistDuration(300) });

  cubeStore.setNarrativeStage('content_reconstruction');
  cubeStore.updateCubePhase('content_reconstruction');
  await delay(500);

  cubeStore.setNarrativeStage('matrix_linking');
  cubeStore.updateCubePhase('matrix_linking');
  
  cabinetStore.setCabinetState('half');
  await delay(500);

  await cubeStore.triggerTwist({ axis: 'x', layer: 0, angle: Math.PI / 2, duration: getTwistDuration(300) });
  await cubeStore.triggerTwist({ axis: 'y', layer: 1, angle: -Math.PI / 2, duration: getTwistDuration(300) });
  await cubeStore.triggerTwist({ axis: 'x', layer: 1, angle: Math.PI / 2, duration: getTwistDuration(300) });
  
  await delay(500);

  cubeStore.setNarrativeStage('final_form');
  cubeStore.updateCubePhase('final_form');
  
  // Fast random layer twists
  for (let i = 0; i < 15; i++) {
    const axes: ('x'|'y'|'z')[] = ['x', 'y', 'z'];
    const layers = [-1, 0, 1];
    const angles = [Math.PI / 2, -Math.PI / 2, Math.PI];
    
    const axis = axes[Math.floor(Math.random() * axes.length)];
    const layer = layers[Math.floor(Math.random() * layers.length)];
    const angle = angles[Math.floor(Math.random() * angles.length)];
    
    await cubeStore.triggerTwist({ axis, layer, angle, duration: 100 });
  }
  
  await delay(100);
  
  // Trigger physical reset underneath the smoke
  cubeStore.triggerCubieReset();
  
  await delay(100);
  
  // End cinematic effect
  cubeStore.setReconstructing(false);
  cabinetStore.setCabinetState('collapsed');

  await delay(500);
  cubeStore.setNarrativeStage('idle');
  cubeStore.setIsAnimating(false);
  cubeStore.setInteractionState('idle');
  
  // reset animation speed to normal after run if it was skipped or fast
  useAppStore.getState().setAnimationSpeed('normal');
};
