from fastapi import APIRouter, Depends

from backend.app.schemas.snapshots import SavedReconstructionSnapshot
from backend.app.services.snapshot_service import SnapshotService


router = APIRouter(prefix="/snapshots", tags=["snapshots"])


SNAPSHOT_LIST_RESPONSE_EXAMPLE = [
    {
        "snapshot_id": "snap_demo_p0a_low_budget_student",
        "source_asset_id": "asset_current_techu_huaian_hotel_candidate",
        "source_task_id": "task_demo_p0a_low_budget_student",
        "card_type": "decision",
        "title": "周末探店备选",
        "saved_summary": "价格和排队情况待确认后再决定。",
        "key_decision_or_action": "确认人均与排队情况",
        "evidence_refs": ["asset_huaian_low_budget_daytrip_ev1"],
        "related_asset_refs": ["asset_huaian_low_budget_daytrip"],
        "saved_at": "2026-05-30T00:00:00Z",
        "user_note": "适合预算内备选",
        "high_risk_domain": False,
        "risk_domain_tags": [],
    }
]


def get_snapshot_service() -> SnapshotService:
    return SnapshotService()


@router.get(
    "",
    response_model=list[SavedReconstructionSnapshot],
    responses={200: {"content": {"application/json": {"example": SNAPSHOT_LIST_RESPONSE_EXAMPLE}}}},
)
def list_snapshots(
    service: SnapshotService = Depends(get_snapshot_service),
) -> list[SavedReconstructionSnapshot]:
    return service.list_snapshots()
