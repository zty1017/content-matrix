import type { AssetCube, CabinetShelf } from "../types/assets";
import cabinetAssetsData from "./cabinetAssets.json";

export const fallbackAssetCubes: Record<string, AssetCube> = cabinetAssetsData.assets as Record<string, AssetCube>;

export const fallbackCabinetShelves: CabinetShelf[] = cabinetAssetsData.shelves as CabinetShelf[];
