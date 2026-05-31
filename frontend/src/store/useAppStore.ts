import { create } from "zustand";

export type AppMode = "current" | "cabinet" | "workshop";
export type DemoMode = "prefer_backend" | "force_fallback";
export type AnimationSpeed = "normal" | "fast" | "skip";
export type ApiStatus = "unknown" | "connected" | "failed" | "testing";

interface AppState {
  currentMode: AppMode;
  demoMode: DemoMode;
  animationSpeed: AnimationSpeed;
  currentDemoContext: string;
  apiBaseUrl: string;
  apiStatus: ApiStatus;
  
  setMode: (mode: AppMode) => void;
  setDemoMode: (mode: DemoMode) => void;
  setAnimationSpeed: (speed: AnimationSpeed) => void;
  setDemoContext: (contextId: string) => void;
  setApiBaseUrl: (url: string) => void;
  testConnection: () => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  currentMode: "current",
  demoMode: "prefer_backend",
  animationSpeed: "normal",
  currentDemoContext: "ctx_low_budget_student",
  apiBaseUrl: "http://localhost:8000", // API default port
  apiStatus: "unknown",

  setMode: (mode) => set({ currentMode: mode }),
  setDemoMode: (mode) => set({ demoMode: mode }),
  setAnimationSpeed: (speed) => set({ animationSpeed: speed }),
  setDemoContext: (contextId) => set({ currentDemoContext: contextId }),
  setApiBaseUrl: (url) => set({ apiBaseUrl: url }),
  testConnection: async () => {
    set({ apiStatus: "testing" });
    try {
      const res = await fetch(`${get().apiBaseUrl}/health`, { method: "GET" });
      if (res.ok) {
        set({ apiStatus: "connected" });
      } else {
        set({ apiStatus: "failed" });
      }
    } catch (e) {
      set({ apiStatus: "failed" });
    }
  }
}));
