from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import urlparse

from backend.app.core.errors import InvalidSourceError
from backend.app.repositories import JsonFixtureRepository

SourceInputType = Literal["preset", "douyin_url", "upload_reference"]

ALLOWED_SOURCE_TYPES = ["preset", "douyin_url", "upload_reference"]


@dataclass(frozen=True)
class SourceResolution:
    resolved_source_id: str
    source_type: SourceInputType
    mapping_id: str
    video_asset_id: str
    task_id: str | None
    demo_user_context_id: str | None
    title: str
    resolution_strategy: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "resolved_source_id": self.resolved_source_id,
            "source_type": self.source_type,
            "mapping_id": self.mapping_id,
            "video_asset_id": self.video_asset_id,
            "task_id": self.task_id,
            "demo_user_context_id": self.demo_user_context_id,
            "title": self.title,
            "resolution_strategy": self.resolution_strategy,
        }


class SourceResolver:
    def __init__(self, repository: JsonFixtureRepository | None = None) -> None:
        self.repository = repository or JsonFixtureRepository()

    def resolve(
        self,
        *,
        source_type: SourceInputType,
        source_id: str | None = None,
        source_url: str | None = None,
        upload_reference_id: str | None = None,
    ) -> SourceResolution:
        if source_type == "preset":
            return self._resolve_identifier(source_type, source_id, field="source_id")
        if source_type == "douyin_url":
            identifier = self._extract_douyin_identifier(source_url)
            return self._resolve_identifier(source_type, identifier, field="source_url")
        if source_type == "upload_reference":
            return self._resolve_identifier(source_type, upload_reference_id, field="upload_reference_id")
        raise self._invalid_source("source_type")

    def _resolve_identifier(
        self,
        source_type: SourceInputType,
        identifier: str | None,
        *,
        field: str,
    ) -> SourceResolution:
        if not identifier:
            raise self._invalid_source(field)

        mapping = self.repository.get_source_mapping(identifier)
        if mapping is None:
            raise self._invalid_source(field)
        return SourceResolution(
            resolved_source_id=identifier,
            source_type=source_type,
            mapping_id=mapping["mapping_id"],
            video_asset_id=mapping["video_asset_id"],
            task_id=mapping.get("task_id"),
            demo_user_context_id=mapping.get("demo_user_context_id"),
            title=mapping.get("title", mapping["video_asset_id"]),
            resolution_strategy=mapping.get("resolution_strategy", "cache_matched"),
        )

    def _extract_douyin_identifier(self, source_url: str | None) -> str:
        if not source_url:
            raise self._invalid_source("source_url")
        parsed = urlparse(source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc.endswith("douyin.com"):
            raise self._invalid_source("source_url")

        for mapping in self.repository.load_source_mappings():
            for key in ("source_id", "mapping_id"):
                identifier = mapping[key]
                if identifier in source_url:
                    return identifier
        raise self._invalid_source("source_url")

    @staticmethod
    def _invalid_source(field: str) -> InvalidSourceError:
        return InvalidSourceError(
            "Unsupported or unmapped source.",
            {"field": field, "allowed": ALLOWED_SOURCE_TYPES},
        )
