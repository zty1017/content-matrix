export type CubeState = "input_ready" | "transforming" | "ready" | "blocked" | "failed";

export type CubeAnimationPhase =
  | "source_resolution"
  | "content_reconstruction"
  | "matrix_linking"
  | "final_form"
  | "needs_confirmation"
  | "error";

export type CubeFaceId =
  | "source"
  | "primary_card"
  | "related_assets"
  | "inferences"
  | "evidence"
  | "snapshot";

export interface CubeFace {
  face_id: CubeFaceId;
  face_type: string;
  title: string;
  status: string;
  target_ref?: { type: string; id: string } | null;
  display_blocks: Array<Record<string, unknown>>;
  action?: Record<string, unknown> | null;
}

export interface CubeProgressStep {
  step_id: string;
  title: string;
  phase: CubeAnimationPhase;
  percent: number;
  status: string;
}

export interface CubeProgress {
  task_id: string;
  cube_state: CubeState;
  animation_phase: CubeAnimationPhase;
  percent: number;
  message: string;
  steps: CubeProgressStep[];
}

export interface CubeView {
  task_id: string;
  video_asset_id: string;
  cube_state: CubeState;
  animation_phase: CubeAnimationPhase;
  source_status: string;
  asset_status: string;
  retrieval_status: string;
  progress: CubeProgress;
  faces: CubeFace[];
  warnings: string[];
}
