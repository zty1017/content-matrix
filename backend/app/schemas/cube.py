from enum import Enum
from typing import Any

from pydantic import Field

from backend.app.schemas.common import FlexibleSchema


class CubeState(str, Enum):
    input_ready = "input_ready"
    transforming = "transforming"
    ready = "ready"
    blocked = "blocked"
    failed = "failed"


class CubeAnimationPhase(str, Enum):
    source_resolution = "source_resolution"
    content_reconstruction = "content_reconstruction"
    matrix_linking = "matrix_linking"
    final_form = "final_form"
    needs_confirmation = "needs_confirmation"
    error = "error"


class CubeFace(FlexibleSchema):
    face_id: str
    face_type: str
    title: str
    status: str
    target_ref: dict[str, str] | None = None
    display_blocks: list[dict[str, Any]] = Field(default_factory=list)
    action: dict[str, Any] | None = None


class CubeProgressStep(FlexibleSchema):
    step_id: str
    title: str
    phase: CubeAnimationPhase
    percent: float
    status: str


class CubeProgress(FlexibleSchema):
    task_id: str
    cube_state: CubeState
    animation_phase: CubeAnimationPhase
    percent: float
    message: str
    steps: list[CubeProgressStep]


class CubeView(FlexibleSchema):
    task_id: str
    video_asset_id: str
    cube_state: CubeState
    animation_phase: CubeAnimationPhase
    source_status: str
    asset_status: str
    retrieval_status: str
    progress: CubeProgress
    faces: list[CubeFace]
    warnings: list[str] = Field(default_factory=list)
