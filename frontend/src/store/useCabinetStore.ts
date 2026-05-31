import { create } from "zustand";
import type { AssetCube, CabinetShelf } from "../types/assets";
import { fallbackAssetCubes, fallbackCabinetShelves } from "../data/fallbackCabinetAssets";
import { loadCustomAssets, saveCustomAssets } from "../lib/localStorage";
import type { UiCubeModel } from "../types/cube";

type CabinetState = "collapsed" | "half" | "expanded";
type RelationPreviewState = "hidden" | "first_order" | "global";

interface CabinetStore {
  cabinetState: CabinetState;
  assets: Record<string, AssetCube>;
  shelves: CabinetShelf[];
  selectedAssetIds: string[];
  previewAssetId: string | null;
  searchQuery: string;
  filterMode: string;
  relationPreviewState: RelationPreviewState;

  setCabinetState: (state: CabinetState) => void;
  setAssets: (assets: Record<string, AssetCube>) => void;
  addAsset: (asset: AssetCube) => void;
  setShelves: (shelves: CabinetShelf[]) => void;
  toggleSelectedAsset: (assetId: string) => void;
  clearSelectedAssets: () => void;
  setPreviewAssetId: (assetId: string | null) => void;
  setSearchQuery: (query: string) => void;
  setFilterMode: (mode: string) => void;
  setRelationPreviewState: (state: RelationPreviewState) => void;
  saveCurrentToCabinet: (cube: UiCubeModel) => void;
}

const initialAssets = { ...fallbackAssetCubes, ...loadCustomAssets() };

export const useCabinetStore = create<CabinetStore>((set) => ({
  cabinetState: "collapsed",
  assets: initialAssets,
  shelves: fallbackCabinetShelves,
  selectedAssetIds: [],
  previewAssetId: null,
  searchQuery: "",
  filterMode: "all",
  relationPreviewState: "hidden",

  setCabinetState: (state) => set({ cabinetState: state }),
  setAssets: (assets) => set({ assets }),
  addAsset: (asset) => 
    set((state) => ({ assets: { ...state.assets, [asset.id]: asset } })),
  setShelves: (shelves) => set({ shelves }),
  toggleSelectedAsset: (assetId) => 
    set((state) => {
      const isSelected = state.selectedAssetIds.includes(assetId);
      return {
        selectedAssetIds: isSelected 
          ? state.selectedAssetIds.filter(id => id !== assetId)
          : [...state.selectedAssetIds, assetId]
      };
    }),
  clearSelectedAssets: () => set({ selectedAssetIds: [] }),
  setPreviewAssetId: (assetId) => set({ previewAssetId: assetId }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setFilterMode: (mode) => set({ filterMode: mode }),
  setRelationPreviewState: (state) => set({ relationPreviewState: state }),
  
  saveCurrentToCabinet: (cube) => {
    const newAssetId = `asset_custom_${Date.now()}`;
    const newAsset: AssetCube = {
      id: newAssetId,
      title: cube.title || "新生成的魔方资产",
      shortSummary: "来源于用户当前重构任务",
      type: "decision",
      status: "formal",
      scenarioTags: ["自建资产", "最新"],
      sourceType: "manual",
      cubeView: cube,
      createdAt: new Date().toISOString()
    };

    set((state) => {
      const updatedAssets = { ...state.assets, [newAssetId]: newAsset };
      
      const updatedShelves = state.shelves.map(shelf => {
        if (shelf.kind === 'recent') {
          return { ...shelf, assetIds: [newAssetId, ...shelf.assetIds] };
        }
        return shelf;
      });

      const customAssets = Object.values(updatedAssets).filter(a => a.id.startsWith('asset_custom_'));
      const customAssetsMap = customAssets.reduce((acc, a) => ({ ...acc, [a.id]: a }), {});
      saveCustomAssets(customAssetsMap);

      return { assets: updatedAssets, shelves: updatedShelves, cabinetState: 'half' };
    });
  }
}));
