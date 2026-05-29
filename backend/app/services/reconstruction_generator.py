from __future__ import annotations

from copy import deepcopy

from backend.app.core.errors import ConstrainedRequestError, NotFoundError
from backend.app.repositories import JsonFixtureRepository
from backend.app.schemas.common import AssetStatus, RetrievalStatus, SourceStatus
from backend.app.schemas.tasks import AssetKind, ReconstructionTask


class ReconstructionGenerator:
    def __init__(self, repository: JsonFixtureRepository | None = None) -> None:
        self.repository = repository or JsonFixtureRepository()

    def generate_card(self, task_id: str) -> ReconstructionTask:
        task = self.repository.get_reconstruction_task(task_id)
        if task is None:
            raise NotFoundError(
                "Reconstruction task was not found.",
                {"resource": "reconstruction_task", "identifier": task_id},
            )
        if task.asset_kind == AssetKind.draft:
            raise ConstrainedRequestError(
                "Draft task must be completed before card generation.",
                {"task_id": task_id, "asset_kind": "draft", "missing": ["confirmed_source_facts"]},
            )
        if task.session_context.high_risk_domain or task.primary_card.high_risk_domain:
            risk_tags = task.session_context.risk_domain_tags or task.primary_card.risk_domain_tags
            raise ConstrainedRequestError(
                "High-risk tasks require user confirmation before card generation.",
                {"task_id": task_id, "high_risk_domain": True, "risk_domain_tags": risk_tags},
            )

        payload = deepcopy(task.model_dump(mode="json"))
        payload["source_status"] = SourceStatus.source_ready.value
        payload["asset_status"] = AssetStatus.asset_complete.value
        payload["retrieval_status"] = RetrievalStatus.retrieval_applied.value
        payload["generated_outputs"] = [
            {
                "output_id": f"out_{task_id}_primary_card",
                "type": "primary_card",
                "status": "ready",
            }
        ]
        generated = ReconstructionTask.model_validate(payload)
        return self.repository.save_runtime_reconstruction_task(generated)
