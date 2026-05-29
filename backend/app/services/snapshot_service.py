from __future__ import annotations

from backend.app.core.errors import ConstrainedRequestError, NotFoundError
from backend.app.repositories import JsonFixtureRepository
from backend.app.schemas.common import AssetStatus
from backend.app.schemas.snapshots import SavedReconstructionSnapshot
from backend.app.schemas.tasks import SaveSnapshotRequest


class SnapshotService:
    def __init__(self, repository: JsonFixtureRepository | None = None) -> None:
        self.repository = repository or JsonFixtureRepository()

    def save_snapshot(self, task_id: str, request: SaveSnapshotRequest) -> SavedReconstructionSnapshot:
        task = self.repository.get_reconstruction_task(task_id)
        if task is None:
            raise NotFoundError(
                "Reconstruction task was not found.",
                {"resource": "reconstruction_task", "identifier": task_id},
            )
        if task.asset_status != AssetStatus.asset_complete:
            raise ConstrainedRequestError(
                "Task card must be generated before saving a snapshot.",
                {"task_id": task_id, "asset_status": task.asset_status.value},
            )

        first_action = task.primary_card.action_entries[0] if task.primary_card.action_entries else {}
        snapshot = SavedReconstructionSnapshot.model_validate(
            {
                "snapshot_id": f"snap_{task.task_id}",
                "source_asset_id": task.video_asset_id,
                "source_task_id": task.task_id,
                "card_type": task.primary_card.card_type.value,
                "title": request.title or task.primary_card.common.get("title") or task.primary_card.display_name or task.task_id,
                "saved_summary": task.primary_card.common.get("summary", ""),
                "key_decision_or_action": first_action.get("label"),
                "evidence_refs": task.primary_card.evidence_refs,
                "related_asset_refs": [asset.related_asset_id for asset in task.related_assets],
                "saved_at": "2026-05-30T00:00:00Z",
                "user_note": request.user_note,
                "high_risk_domain": task.primary_card.high_risk_domain or task.session_context.high_risk_domain,
                "risk_domain_tags": task.primary_card.risk_domain_tags or task.session_context.risk_domain_tags,
            }
        )
        return self.repository.save_runtime_reconstruction_snapshot(snapshot)
