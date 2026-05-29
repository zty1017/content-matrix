from __future__ import annotations

from backend.app.core.errors import NotFoundError
from backend.app.repositories import JsonFixtureRepository
from backend.app.schemas import DemoUserAssetContext, VideoContentAsset


class RetrievalService:
    def __init__(self, repository: JsonFixtureRepository | None = None) -> None:
        self.repository = repository or JsonFixtureRepository()

    def list_demo_contexts(self) -> list[DemoUserAssetContext]:
        return sorted(
            self.repository.load_demo_user_asset_contexts(),
            key=lambda context: context.demo_user_context_id,
        )

    def get_demo_context(self, context_id: str) -> DemoUserAssetContext:
        context = self.repository.get_demo_user_asset_context(context_id)
        if context is None:
            raise NotFoundError(
                "Requested demo context was not found.",
                {"resource": "demo_user_asset_context", "identifier": context_id},
            )
        return context

    def search_assets(self, *, query: str | None = None, tags: list[str] | None = None) -> list[VideoContentAsset]:
        normalized_query = self._blank_to_none(query)
        normalized_tags = [tag.strip() for tag in tags or [] if tag.strip()]
        if normalized_query is None and not normalized_tags:
            return []
        return self.repository.search_video_content_assets(
            query=normalized_query,
            tags=normalized_tags,
        )

    @staticmethod
    def _blank_to_none(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None
