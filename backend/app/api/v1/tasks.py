from fastapi import APIRouter, Body, Depends

from backend.app.schemas.errors import ApiErrorResponse
from backend.app.schemas.snapshots import SavedReconstructionSnapshot
from backend.app.schemas.tasks import CreateReconstructionTaskRequest, ReconstructionTask, SaveSnapshotRequest
from backend.app.services.reconstruction_generator import ReconstructionGenerator
from backend.app.services.snapshot_service import SnapshotService
from backend.app.services.task_state import TaskStateService

router = APIRouter(prefix="/tasks", tags=["tasks"])

TASK_CREATE_EXAMPLES = {
    "from_resolved_preset": {
        "summary": "Create a runtime task from /source/resolve output",
        "value": {
            "source_id": "preset_current_techu_huaian_hotel_candidate",
            "source_type": "preset",
            "session_context": {
                "raw_text": "周六下午 2 小时，预算 100 元以内，不想排队。",
                "goals": ["短时间体验本地特色"],
                "constraints": ["2 小时以内", "预算 100 元以内"],
                "preferences": ["少排队"],
                "scenario": "本地生活/探店决策",
            },
        },
    }
}

TASK_CREATE_RESPONSE_EXAMPLE = {
    "task_id": "task_runtime_preset_current_techu_huaian_hotel_candidate",
    "video_asset_id": "asset_current_techu_huaian_hotel_candidate",
    "session_context": {"raw_text": "周六下午 2 小时，预算 100 元以内，不想排队。"},
    "source_status": "cache_matched",
    "asset_status": "basic_ready",
    "retrieval_status": "retrieval_matched",
    "primary_card": {
        "card_type": "decision",
        "common": {"title": "这条探店视频适合我周六下午去吗？"},
        "specific": {},
        "evidence_refs": [],
        "action_entries": [],
    },
    "generated_outputs": [],
}

TASK_DETAIL_RESPONSE_EXAMPLE = TASK_CREATE_RESPONSE_EXAMPLE

GENERATE_CARD_RESPONSE_EXAMPLE = {
    **TASK_CREATE_RESPONSE_EXAMPLE,
    "asset_status": "asset_complete",
    "retrieval_status": "retrieval_applied",
    "generated_outputs": [
        {
            "output_id": "out_task_runtime_preset_current_techu_huaian_hotel_candidate_primary_card",
            "type": "primary_card",
            "status": "ready",
        }
    ],
}

SAVE_SNAPSHOT_EXAMPLES = {
    "weekend_candidate": {
        "summary": "Save generated card as a weekend candidate",
        "value": {"title": "周末探店备选", "user_note": "保留为周末备选"},
    }
}

SAVE_SNAPSHOT_RESPONSE_EXAMPLE = {
    "snapshot_id": "snap_task_runtime_preset_current_techu_huaian_hotel_candidate",
    "source_asset_id": "asset_current_techu_huaian_hotel_candidate",
    "source_task_id": "task_runtime_preset_current_techu_huaian_hotel_candidate",
    "card_type": "decision",
    "title": "周末探店备选",
    "saved_summary": "基于当前视频事实、你的本次预算与历史低预算资产，系统生成有条件判断。",
    "key_decision_or_action": "确认人均与排队情况",
    "evidence_refs": ["asset_huaian_low_budget_daytrip_ev1"],
    "related_asset_refs": ["asset_huaian_low_budget_daytrip"],
    "saved_at": "2026-05-30T00:00:00Z",
    "user_note": "保留为周末备选",
    "high_risk_domain": False,
    "risk_domain_tags": [],
}


def get_task_state_service() -> TaskStateService:
    return TaskStateService()


def get_reconstruction_generator() -> ReconstructionGenerator:
    return ReconstructionGenerator()


def get_snapshot_service() -> SnapshotService:
    return SnapshotService()


@router.post(
    "",
    response_model=ReconstructionTask,
    responses={200: {"content": {"application/json": {"example": TASK_CREATE_RESPONSE_EXAMPLE}}}, 400: {"model": ApiErrorResponse}, 404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
)
def create_task(
    request: CreateReconstructionTaskRequest = Body(openapi_examples=TASK_CREATE_EXAMPLES),
    service: TaskStateService = Depends(get_task_state_service),
) -> ReconstructionTask:
    return service.create_task(request)


@router.get(
    "/{task_id}",
    response_model=ReconstructionTask,
    responses={
        200: {"content": {"application/json": {"example": TASK_DETAIL_RESPONSE_EXAMPLE}}},
        404: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
def get_task(
    task_id: str,
    service: TaskStateService = Depends(get_task_state_service),
) -> ReconstructionTask:
    return service.get_task(task_id)


@router.post(
    "/{task_id}/generate-card",
    response_model=ReconstructionTask,
    responses={200: {"content": {"application/json": {"example": GENERATE_CARD_RESPONSE_EXAMPLE}}}, 404: {"model": ApiErrorResponse}, 422: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
)
def generate_card(
    task_id: str,
    generator: ReconstructionGenerator = Depends(get_reconstruction_generator),
) -> ReconstructionTask:
    return generator.generate_card(task_id)


@router.post(
    "/{task_id}/save-snapshot",
    response_model=SavedReconstructionSnapshot,
    responses={200: {"content": {"application/json": {"example": SAVE_SNAPSHOT_RESPONSE_EXAMPLE}}}, 404: {"model": ApiErrorResponse}, 422: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
)
def save_snapshot(
    task_id: str,
    request: SaveSnapshotRequest = Body(openapi_examples=SAVE_SNAPSHOT_EXAMPLES),
    service: SnapshotService = Depends(get_snapshot_service),
) -> SavedReconstructionSnapshot:
    return service.save_snapshot(task_id, request)
