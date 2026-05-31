import type { AssetCube } from '../types/assets';

const ASSETS_STORAGE_KEY = 'content_matrix_custom_assets';

export const saveCustomAssets = (assets: Record<string, AssetCube>) => {
  try {
    localStorage.setItem(ASSETS_STORAGE_KEY, JSON.stringify(assets));
  } catch (error) {
    console.error('Failed to save assets to localStorage', error);
  }
};

export const loadCustomAssets = (): Record<string, AssetCube> => {
  try {
    const data = localStorage.getItem(ASSETS_STORAGE_KEY);
    return data ? JSON.parse(data) : {};
  } catch (error) {
    console.error('Failed to load assets from localStorage', error);
    return {};
  }
};
