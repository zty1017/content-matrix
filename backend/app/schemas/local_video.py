from enum import Enum
from typing import Any

from pydantic import Field

from backend.app.schemas.assets import VideoContentAsset
from backend.app.schemas.common import FlexibleSchema


class LocalVideoParseMode(str, Enum):
    fallback = "fallback"
    doubao_if_configured = "doubao_if_configured"


class LocalVideoParseRequest(FlexibleSchema):
    local_reference_id: str
    parse_mode: LocalVideoParseMode = LocalVideoParseMode.fallback
    demo_user_context_id: str | None = None


class LocalVideoAsrResult(FlexibleSchema):
    provider: str
    is_fallback: bool
    transcript: str
    transcript_path: str | None = None
    detail: dict[str, Any] = Field(default_factory=dict)


class LocalVideoParseResult(FlexibleSchema):
    local_reference_id: str
    parse_mode: LocalVideoParseMode
    content_type: str
    title: str
    asset: VideoContentAsset
    asr: LocalVideoAsrResult
    display_blocks: list[dict[str, Any]]
    demo_user_context_id: str | None = None
    warnings: list[str] = Field(default_factory=list)
