import { create } from "zustand";
import type { WorkshopBlock, OutputStyle } from "../types/workshop";
import type { UiCubeModel } from "../types/cube";

type WorkshopStage = "idle" | "disassembling" | "recombining" | "result";

interface WorkshopStore {
  selectedAssets: string[];
  semanticBlocks: WorkshopBlock[];
  selectedBlockIds: string[];
  recombinationTarget: string;
  outputStyle: OutputStyle;
  workshopStage: WorkshopStage;
  resultCube: UiCubeModel | null;

  setSelectedAssets: (assetIds: string[]) => void;
  setSemanticBlocks: (blocks: WorkshopBlock[]) => void;
  toggleSelectedBlock: (blockId: string) => void;
  setRecombinationTarget: (target: string) => void;
  setOutputStyle: (style: OutputStyle) => void;
  setWorkshopStage: (stage: WorkshopStage) => void;
  setResultCube: (cube: UiCubeModel | null) => void;
  resetWorkshop: () => void;
}

export const useWorkshopStore = create<WorkshopStore>((set) => ({
  selectedAssets: [],
  semanticBlocks: [],
  selectedBlockIds: [],
  recombinationTarget: "",
  outputStyle: "compact_card",
  workshopStage: "idle",
  resultCube: null,

  setSelectedAssets: (assetIds) => set({ selectedAssets: assetIds }),
  setSemanticBlocks: (blocks) => set({ semanticBlocks: blocks }),
  toggleSelectedBlock: (blockId) => 
    set((state) => {
      const isSelected = state.selectedBlockIds.includes(blockId);
      return {
        selectedBlockIds: isSelected
          ? state.selectedBlockIds.filter(id => id !== blockId)
          : [...state.selectedBlockIds, blockId]
      };
    }),
  setRecombinationTarget: (target) => set({ recombinationTarget: target }),
  setOutputStyle: (style) => set({ outputStyle: style }),
  setWorkshopStage: (stage) => set({ workshopStage: stage }),
  setResultCube: (cube) => set({ resultCube: cube }),
  resetWorkshop: () => set({
    selectedAssets: [],
    semanticBlocks: [],
    selectedBlockIds: [],
    recombinationTarget: "",
    outputStyle: "compact_card",
    workshopStage: "idle",
    resultCube: null
  })
}));
