from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.core.errors import NotFoundError
from backend.app.repositories import JsonFixtureRepository
from backend.app.schemas.assets import AssetSource, SourceType, VideoContentAsset
from backend.app.schemas.common import AssetStatus, ConfidenceLevel, ReconstructionType
from backend.app.services.source_resolver import SourceResolution, SourceResolver


@dataclass(frozen=True)
class AssetBuildResult:
    asset_id: str
    status: AssetStatus
    source_resolution: SourceResolution
    asset: VideoContentAsset

    def to_payload(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "status": self.status,
            "source_resolution": self.source_resolution.to_payload(),
            "asset": self.asset.model_dump(mode="json"),
        }


class AssetBuilder:
    def __init__(self, repository: JsonFixtureRepository | None = None) -> None:
        self.repository = repository or JsonFixtureRepository()
        self.source_resolver = SourceResolver(self.repository)

    def build_from_resolved_source(self, resolved_source_id: str) -> AssetBuildResult:
        source_resolution = self.source_resolver.resolve(source_type="preset", source_id=resolved_source_id)
        asset = self.get_asset(source_resolution.video_asset_id)
        return AssetBuildResult(
            asset_id=asset.asset_id,
            status=AssetStatus.asset_complete,
            source_resolution=source_resolution,
            asset=asset,
        )

    def get_asset(self, asset_id: str) -> VideoContentAsset:
        asset = self.repository.get_video_content_asset(asset_id)
        if asset is not None:
            return asset

        mapping = self._mapping_for_asset(asset_id)
        if mapping is None:
            raise NotFoundError(
                "Requested asset was not found.",
                {"resource": "video_content_asset", "identifier": asset_id},
            )
        return self._asset_from_mapping_task(mapping)

    def _mapping_for_asset(self, asset_id: str) -> dict[str, Any] | None:
        for mapping in self.repository.load_source_mappings():
            if mapping["video_asset_id"] == asset_id:
                return mapping
        return None

    def _asset_from_mapping_task(self, mapping: dict[str, Any]) -> VideoContentAsset:
        task = self.repository.get_reconstruction_task(mapping.get("task_id", ""), include_runtime=False)
        if task is None:
            raise NotFoundError(
                "Requested asset was not found.",
                {"resource": "video_content_asset", "identifier": mapping["video_asset_id"]},
            )

        specific = task.primary_card.specific
        key_points = specific.get("key_factors") or specific.get("needs_confirmation") or []
        return VideoContentAsset(
            asset_id=mapping["video_asset_id"],
            source=AssetSource(
                type=SourceType.local_mapping,
                title=mapping.get("title", task.primary_card.common.get("title", mapping["video_asset_id"])),
                mapping_id=mapping["mapping_id"],
            ),
            reconstruction_type=ReconstructionType(task.primary_card.card_type.value),
            content_domain_tags=list(task.session_context.goals + task.session_context.constraints + task.session_context.preferences),
            base_summary=task.primary_card.common.get("summary", ""),
            key_points=list(key_points),
            evidence=list(task.evidence),
            facts=[],
            confidence_level=ConfidenceLevel.medium,
            needs_confirmation=True,
            strategy_metadata={"source_mapping_id": mapping["mapping_id"], "task_id": task.task_id},
        )
