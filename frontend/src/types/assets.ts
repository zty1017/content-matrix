import type { UiCubeModel } from "./cube";

export type AssetStatus = "formal" | "draft" | "needs_confirmation";
export type AssetType = "knowledge" | "decision" | "experience" | "procedure" | "script";

export interface AssetCube {
  id: string;
  title: string;
  shortSummary: string;
  type: AssetType;
  status: AssetStatus;
  scenarioTags: string[];
  sourceType: "douyin" | "local_video" | "manual" | "demo_seed" | "fallback";
  cover?: string;
  cubeView?: UiCubeModel;
  usedCount?: number;
  lastUsedFor?: string;
  currentTaskReferenced?: boolean;
  manuallyConfirmed?: boolean;
  highRisk?: boolean;
  needsConfirmation?: boolean;
  createdAt?: string;
}

export type CabinetShelfKind = "current_related" | "recent" | "frequent" | "draft" | "type" | "scenario" | "search";

export interface CabinetShelf {
  id: string;
  title: string;
  description?: string;
  assetIds: string[];
  kind: CabinetShelfKind;
}
