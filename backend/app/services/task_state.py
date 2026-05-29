from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime

from backend.app.core.errors import InvalidSourceError, NotFoundError
from backend.app.repositories import JsonFixtureRepository
from backend.app.schemas.common import AssetStatus, RetrievalStatus, SourceStatus
from backend.app.services.source_resolver import SourceInputType
from backend.app.schemas.tasks import CreateReconstructionTaskRequest, ReconstructionTask


class TaskStateService:
    def __init__(self, repository: JsonFixtureRepository | None = None) -> None:
        self.repository = repository or JsonFixtureRepository()

    def create_task(self, request: CreateReconstructionTaskRequest) -> ReconstructionTask:
        mapping = self.repository.get_source_mapping(request.source_id)
        if mapping is None:
            raise InvalidSourceError(
                "Source could not be resolved to a reconstruction task.",
                {"resource": "source_mapping", "identifier": request.source_id},
            )
        if request.source_type is not None:
            expected_source_type = self._public_source_type(mapping["source_type"])
            if expected_source_type != request.source_type:
                raise InvalidSourceError(
                    "Source type does not match the configured mapping.",
                    {"field": "source_type", "expected": expected_source_type, "received": request.source_type},
                )

        base_task = self.repository.get_reconstruction_task(mapping["task_id"])
        if base_task is None:
            raise NotFoundError(
                "Reconstruction task was not found.",
                {"resource": "reconstruction_task", "identifier": mapping["task_id"]},
            )

        payload = deepcopy(base_task.model_dump(mode="json"))
        payload["task_id"] = self._runtime_task_id(mapping["source_id"])
        payload["video_asset_id"] = mapping["video_asset_id"]
        payload["demo_user_context_id"] = request.demo_user_context_id or mapping.get("demo_user_context_id")
        payload["source_status"] = mapping.get("resolution_strategy") or SourceStatus.cache_matched.value
        payload["asset_status"] = AssetStatus.basic_ready.value
        payload["retrieval_status"] = RetrievalStatus.retrieval_matched.value
        payload["generated_outputs"] = []
        payload["created_at"] = self._now_iso()
        payload["updated_at"] = payload["created_at"]
        if request.session_context is not None:
            payload["session_context"] = request.session_context.model_dump(mode="json")
        if request.asset_kind is not None:
            payload["asset_kind"] = request.asset_kind.value

        task = ReconstructionTask.model_validate(payload)
        return self.repository.save_runtime_reconstruction_task(task)

    def get_task(self, task_id: str) -> ReconstructionTask:
        task = self.repository.get_reconstruction_task(task_id)
        if task is None:
            raise NotFoundError(
                "Reconstruction task was not found.",
                {"resource": "reconstruction_task", "identifier": task_id},
            )
        return task

    @staticmethod
    def _public_source_type(mapping_source_type: str) -> SourceInputType:
        if mapping_source_type == "preset_video":
            return "preset"
        if mapping_source_type in {"preset", "douyin_url", "upload_reference"}:
            return mapping_source_type
        return "preset"

    def _runtime_task_id(self, source_id: str) -> str:
        prefix = f"task_runtime_{source_id}"
        existing_ids = {task.task_id for task in self.repository.load_reconstruction_tasks()}
        if prefix not in existing_ids:
            return prefix
        suffix = 2
        while f"{prefix}_{suffix}" in existing_ids:
            suffix += 1
        return f"{prefix}_{suffix}"

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
