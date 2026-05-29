from enum import Enum
from typing import Any

from pydantic import Field, model_validator

from backend.app.schemas.common import ConfidenceLevel, FlexibleSchema, Metadata, ReconstructionType


class SourceType(str, Enum):
    douyin_link = "douyin_link"
    local_mapping = "local_mapping"
    preset_video = "preset_video"
    upload_video = "upload_video"
    upload_audio = "upload_audio"
    text_only = "text_only"
    demo_seed = "demo_seed"


class EvidenceSourceType(str, Enum):
    video_explicit = "video_explicit"
    historical_asset = "historical_asset"
    ai_inference = "ai_inference"
    needs_user_confirmation = "needs_user_confirmation"


class EvidenceOrigin(str, Enum):
    title = "title"
    description = "description"
    asr = "asr"
    subtitle = "subtitle"
    ocr = "ocr"
    keyframe = "keyframe"
    historical_asset = "historical_asset"
    model_inference = "model_inference"
    user_input = "user_input"
    demo_seed = "demo_seed"


class TimestampRange(FlexibleSchema):
    start: float | None = None
    end: float | None = None


class AssetSource(FlexibleSchema):
    type: SourceType
    title: str
    original_url: str | None = None
    canonical_url: str | None = None
    local_path: str | None = None
    mapping_id: str | None = None
    cover_path: str | None = None
    duration_seconds: float | None = None
    resolved_at: str | None = None


class EvidenceItem(FlexibleSchema):
    evidence_id: str
    source_type: EvidenceSourceType
    content: str
    origin: EvidenceOrigin
    confidence: ConfidenceLevel
    needs_confirmation: bool
    timestamp_range: TimestampRange | None = None
    high_risk_domain: bool = False
    risk_domain_tags: list[str] = Field(default_factory=list)


class FactItem(FlexibleSchema):
    fact_id: str
    type: str
    content: str
    evidence_refs: list[str]
    entities: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel | None = None


class VideoContentAsset(FlexibleSchema):
    asset_id: str
    source: AssetSource
    reconstruction_type: ReconstructionType
    content_domain_tags: list[str]
    base_summary: str
    key_points: list[str]
    evidence: list[EvidenceItem]
    facts: list[FactItem]
    confidence_level: ConfidenceLevel
    is_draft: bool = False
    needs_confirmation: bool = False
    custom_blocks: list[dict[str, Any]] = Field(default_factory=list)
    strategy_metadata: Metadata = Field(default_factory=dict)
    demo_metadata: Metadata = Field(default_factory=dict)
    high_risk_domain: bool = False
    risk_domain_tags: list[str] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


class DraftVideoContentAsset(VideoContentAsset):
    is_draft: bool = True
    needs_confirmation: bool = True
    upgrade_conditions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_draft_contract(self) -> "DraftVideoContentAsset":
        if not self.is_draft:
            raise ValueError("DraftVideoContentAsset requires is_draft=true")
        if not self.needs_confirmation:
            raise ValueError("DraftVideoContentAsset requires needs_confirmation=true")
        if self.confidence_level == ConfidenceLevel.high:
            raise ValueError("DraftVideoContentAsset confidence_level must be low or medium")
        return self
