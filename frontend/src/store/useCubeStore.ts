import { create } from "zustand";
import type { UiCubeModel } from "../types/cube";
import type { CubeAnimationPhase, CubeFaceId } from "../types/api";

type CubeInteractionState = "idle" | "dragging" | "animating";

export interface TwistEvent {
  id: string;
  axis: 'x' | 'y' | 'z';
  layer: number; // -1, 0, 1
  angle: number; // 弧度，例如 Math.PI / 2
  duration?: number;
}

interface CubeStore {
  currentCubeView: UiCubeModel | null;
  selectedFaceId: CubeFaceId | null;
  cubeInteractionState: CubeInteractionState;
  isAnimating: boolean;
  narrativeStage: string;
  processEvents: string[];
  twistEvent: TwistEvent | null;
  isReconstructing: boolean;
  cubieResetTrigger: number;

  setCurrentCubeView: (cube: UiCubeModel | null) => void;
  updateCubePhase: (phase: CubeAnimationPhase) => void;
  setSelectedFaceId: (faceId: CubeFaceId | null) => void;
  setInteractionState: (state: CubeInteractionState) => void;
  setIsAnimating: (isAnimating: boolean) => void;
  setNarrativeStage: (stage: string) => void;
  addProcessEvent: (event: string) => void;
  triggerTwist: (event: Omit<TwistEvent, 'id'>) => Promise<void>;
  clearTwistEvent: () => void;
  setReconstructing: (val: boolean) => void;
  triggerCubieReset: () => void;
  resetCubeStore: () => void;
}

export const useCubeStore = create<CubeStore>((set) => ({
  currentCubeView: null,
  selectedFaceId: null,
  cubeInteractionState: "idle",
  isAnimating: false,
  narrativeStage: "idle",
  processEvents: [],
  twistEvent: null,
  isReconstructing: false,
  cubieResetTrigger: 0,

  setCurrentCubeView: (cube) => set({ currentCubeView: cube }),
  updateCubePhase: (phase) => 
    set((state) => ({
      currentCubeView: state.currentCubeView ? { ...state.currentCubeView, phase } : null
    })),
  setSelectedFaceId: (faceId) => set({ selectedFaceId: faceId }),
  setInteractionState: (state) => set({ cubeInteractionState: state }),
  setIsAnimating: (isAnimating) => set({ isAnimating }),
  setNarrativeStage: (stage) => set({ narrativeStage: stage }),
  addProcessEvent: (event) => set((state) => ({ processEvents: [...state.processEvents, event] })),
  
  triggerTwist: (event) => {
    return new Promise((resolve) => {
      set({ twistEvent: { ...event, id: Math.random().toString(36).substring(7) } });
      setTimeout(() => {
        resolve();
      }, event.duration || 600);
    });
  },
  clearTwistEvent: () => set({ twistEvent: null }),
  setReconstructing: (val) => set({ isReconstructing: val }),
  triggerCubieReset: () => set((state) => ({ cubieResetTrigger: state.cubieResetTrigger + 1 })),

  resetCubeStore: () => set({
    currentCubeView: null,
    selectedFaceId: null,
    cubeInteractionState: "idle",
    isAnimating: false,
    narrativeStage: "idle",
    processEvents: [],
    twistEvent: null,
    isReconstructing: false,
    cubieResetTrigger: 0
  })
}));
