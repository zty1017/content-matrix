// types/index.ts

export interface DemoContext {
  context_id: string;
  name: string;
  description: string;
  task_id: string;
}

export interface CardCommon {
  title: string;
  summary: string;
}

export interface CardSpecific {
  decision_level: string;
  one_sentence_judgement: string;
  key_factors: string[];
  needs_confirmation: string[];
}

export interface DecisionCardData {
  common: CardCommon;
  specific: CardSpecific;
}

export interface RelatedAsset {
  asset_id: string;
  title: string;
  influence_type: 'supplement' | 'preference_adaptation' | 'conflict_warning';
  explanation: string;
}

export interface ReconstructionTaskData {
  task_id: string;
  primary_card: DecisionCardData;
  related_assets: RelatedAsset[];
  evidence_refs: string[];
  action_entries: string[];
  source_asset?: unknown;
}
