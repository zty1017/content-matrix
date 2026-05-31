export type WorkshopBlockType =
  | "summary"
  | "evidence"
  | "preference"
  | "constraint"
  | "tag"
  | "inference"
  | "source"
  | "script_hook";

export interface WorkshopBlock {
  id: string;
  type: WorkshopBlockType;
  title: string;
  content: string;
  sourceAssetId: string;
  selected: boolean;
  weight?: number;
  confidence?: "high" | "medium" | "low";
  needsConfirmation?: boolean;
}

export type OutputStyle =
  | "compact_card"
  | "decision_advice"
  | "knowledge_explanation"
  | "script_reuse"
  | "evidence_strict";
