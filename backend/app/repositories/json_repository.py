from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from backend.app.core.errors import FixtureDataError
from backend.app.schemas.assets import VideoContentAsset
from backend.app.schemas.demo_contexts import DemoUserAssetContext
from backend.app.schemas.snapshots import SavedReconstructionSnapshot
from backend.app.schemas.tasks import ReconstructionTask


class FixtureRepositoryError(FixtureDataError):
    def __init__(self, message: str) -> None:
        self.reason = message
        super().__init__(
            "Fixture data could not be loaded.",
            {"reason": message},
        )

    def __str__(self) -> str:
        return self.reason


ModelT = TypeVar("ModelT", bound=BaseModel)


class JsonFixtureRepository:
    def __init__(self, fixtures_dir: Path | None = None, runtime_dir: Path | None = None) -> None:
        data_dir = Path(__file__).resolve().parents[1] / "data"
        self.fixtures_dir = fixtures_dir or data_dir / "fixtures"
        self.runtime_dir = runtime_dir or data_dir / "runtime"

    def load_video_content_assets(self) -> list[VideoContentAsset]:
        return self._load_models(self.fixtures_dir / "video_content_assets.json", VideoContentAsset)

    def get_video_content_asset(self, asset_id: str) -> VideoContentAsset | None:
        return self._find_by_id(self.load_video_content_assets(), "asset_id", asset_id)

    def search_video_content_assets(
        self,
        *,
        query: str | None = None,
        tags: list[str] | None = None,
        asset_ids: list[str] | None = None,
    ) -> list[VideoContentAsset]:
        normalized_query = query.casefold() if query else None
        tag_set = set(tags or [])
        asset_id_set = set(asset_ids or [])
        matches: list[VideoContentAsset] = []

        for asset in self.load_video_content_assets():
            if asset_id_set and asset.asset_id not in asset_id_set:
                continue
            if tag_set and not tag_set.issubset(asset.content_domain_tags):
                continue
            if normalized_query and normalized_query not in self._asset_search_text(asset):
                continue
            matches.append(asset)

        return sorted(matches, key=lambda item: item.asset_id)

    def load_demo_user_asset_contexts(self) -> list[DemoUserAssetContext]:
        return self._load_models(self.fixtures_dir / "demo_user_asset_contexts.json", DemoUserAssetContext)

    def get_demo_user_asset_context(self, demo_user_context_id: str) -> DemoUserAssetContext | None:
        return self._find_by_id(
            self.load_demo_user_asset_contexts(),
            "demo_user_context_id",
            demo_user_context_id,
        )

    def load_reconstruction_tasks(self, *, include_runtime: bool = True) -> list[ReconstructionTask]:
        fixtures = self._load_models(self.fixtures_dir / "reconstruction_tasks.json", ReconstructionTask)
        if not include_runtime:
            return fixtures
        runtime = self._load_runtime_models("reconstruction_tasks.json", ReconstructionTask)
        return self._merge_by_id(fixtures, runtime, "task_id")

    def get_reconstruction_task(self, task_id: str, *, include_runtime: bool = True) -> ReconstructionTask | None:
        return self._find_by_id(self.load_reconstruction_tasks(include_runtime=include_runtime), "task_id", task_id)

    def save_runtime_reconstruction_task(self, task: ReconstructionTask) -> ReconstructionTask:
        return self._upsert_runtime_model("reconstruction_tasks.json", task, "task_id")

    def load_saved_reconstruction_snapshots(
        self,
        *,
        include_runtime: bool = True,
    ) -> list[SavedReconstructionSnapshot]:
        fixtures = self._load_models(
            self.fixtures_dir / "saved_reconstruction_snapshots.json",
            SavedReconstructionSnapshot,
        )
        if not include_runtime:
            return fixtures
        runtime = self._load_runtime_models("saved_reconstruction_snapshots.json", SavedReconstructionSnapshot)
        return self._merge_by_id(fixtures, runtime, "snapshot_id")

    def get_saved_reconstruction_snapshot(
        self,
        snapshot_id: str,
        *,
        include_runtime: bool = True,
    ) -> SavedReconstructionSnapshot | None:
        return self._find_by_id(
            self.load_saved_reconstruction_snapshots(include_runtime=include_runtime),
            "snapshot_id",
            snapshot_id,
        )

    def save_runtime_reconstruction_snapshot(
        self,
        snapshot: SavedReconstructionSnapshot,
    ) -> SavedReconstructionSnapshot:
        return self._upsert_runtime_model("saved_reconstruction_snapshots.json", snapshot, "snapshot_id")

    def load_source_mappings(self) -> list[dict[str, Any]]:
        records = self._load_json_list(self.fixtures_dir / "source_mappings.json")
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise FixtureRepositoryError(f"source_mappings.json item {index} must be an object")
            missing = {"mapping_id", "source_type", "source_id", "video_asset_id"} - record.keys()
            if missing:
                raise FixtureRepositoryError(
                    f"source_mappings.json item {index} missing required keys: {sorted(missing)}"
                )
        return sorted(records, key=lambda item: item["mapping_id"])

    def get_source_mapping(self, source_id: str) -> dict[str, Any] | None:
        for mapping in self.load_source_mappings():
            if mapping["source_id"] == source_id or mapping["mapping_id"] == source_id:
                return mapping
        return None

    def _load_models(self, path: Path, model: type[ModelT]) -> list[ModelT]:
        records = self._load_json_list(path)
        try:
            return [model.model_validate(record) for record in records]
        except ValidationError as exc:
            raise FixtureRepositoryError(f"Invalid records in {path.name}: {exc}") from exc

    def _load_runtime_models(self, filename: str, model: type[ModelT]) -> list[ModelT]:
        path = self.runtime_dir / filename
        if not path.exists():
            return []
        return self._load_models(path, model)

    def _load_json_list(self, path: Path) -> list[Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FixtureRepositoryError(f"Missing JSON data file: {path}") from exc
        except json.JSONDecodeError as exc:
            raise FixtureRepositoryError(f"Malformed JSON data file: {path}: {exc.msg}") from exc
        if not isinstance(payload, list):
            raise FixtureRepositoryError(f"JSON data file must contain a list: {path}")
        return payload

    def _upsert_runtime_model(self, filename: str, model: ModelT, id_field: str) -> ModelT:
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        path = self.runtime_dir / filename
        existing = self._load_runtime_models(filename, type(model))
        by_id = {getattr(item, id_field): item for item in existing}
        by_id[getattr(model, id_field)] = model
        ordered = [by_id[item_id] for item_id in sorted(by_id)]
        path.write_text(
            json.dumps([item.model_dump(mode="json") for item in ordered], ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        return model

    @staticmethod
    def _find_by_id(items: list[ModelT], id_field: str, expected_id: str) -> ModelT | None:
        for item in items:
            if getattr(item, id_field) == expected_id:
                return item
        return None

    @staticmethod
    def _merge_by_id(fixtures: list[ModelT], runtime: list[ModelT], id_field: str) -> list[ModelT]:
        merged = {getattr(item, id_field): item for item in fixtures}
        merged.update({getattr(item, id_field): item for item in runtime})
        return [merged[item_id] for item_id in sorted(merged)]

    @staticmethod
    def _asset_search_text(asset: VideoContentAsset) -> str:
        parts = [
            asset.asset_id,
            asset.source.title,
            asset.base_summary,
            *asset.content_domain_tags,
            *asset.key_points,
        ]
        return "\n".join(parts).casefold()
