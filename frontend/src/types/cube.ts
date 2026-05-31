import type { CubeState, CubeAnimationPhase, CubeFaceId, CubeProgress } from "./api";

export type UiDetailBlockType =
  | "summary"
  | "key_points"
  | "actions"
  | "evidence"
  | "related_assets"
  | "inferences"
  | "source_preview"
  | "snapshot_form"
  | "custom";

export interface UiDetailBlock {
  type: UiDetailBlockType;
  title: string;
  items?: string[];
  data?: unknown;
}

export type UiFaceStatus = "empty" | "loading" | "ready" | "needs_confirmation" | "blocked" | "failed" | "disabled";
export type UiFaceAccent = "cyan" | "blue" | "violet" | "amber" | "red" | "neutral";

export interface UiCubeFace {
  id: CubeFaceId;
  label: string;
  subtitle?: string;
  status: UiFaceStatus;
  icon: string;
  accent: UiFaceAccent;
  summaryItems: string[];
  detailBlocks: UiDetailBlock[];
  isAiExtracted?: boolean;
  isManuallyEnhanced?: boolean;
  isConfirmed?: boolean;
  needsConfirmation?: boolean;
  highRisk?: boolean;
}

export interface UiCubeModel {
  taskId: string;
  assetId?: string;
  title?: string;
  state: CubeState;
  phase: CubeAnimationPhase;
  faces?: Record<CubeFaceId, UiCubeFace>;
  progress?: CubeProgress;
  referencedAssetIds?: string[];
  warnings?: string[];
}
