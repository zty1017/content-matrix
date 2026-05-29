from enum import Enum
from typing import Any

from pydantic import Field

from backend.app.schemas.assets import EvidenceItem
from backend.app.schemas.common import (
    AssetStatus,
    CardType,
    ConfidenceLevel,
    FlexibleSchema,
    RetrievalStatus,
    SourceStatus,
)


class AssetKind(str, Enum):
    formal = "formal"
    draft = "draft"


class InfluenceType(str, Enum):
    supplement = "supplement"
    preference_adaptation = "preference_adaptation"
    conflict_warning = "conflict_warning"


class SessionContext(FlexibleSchema):
    raw_text: str | None = None
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    scenario: str | None = None
    high_risk_domain: bool = False
    risk_domain_tags: list[str] = Field(default_factory=list)


class RelatedAsset(FlexibleSchema):
    related_asset_id: str
    title: str
    match_reason: str
    influence_type: InfluenceType
    influence_summary: str
    affected_card_sections: list[str]
    evidence_refs: list[str]
    match_score: float | None = None
    confidence_level: ConfidenceLevel | None = None


class InferenceItem(FlexibleSchema):
    inference_id: str
    type: str
    content: str
    evidence_refs: list[str]
    confidence: ConfidenceLevel
    related_asset_refs: list[str] = Field(default_factory=list)
    needs_confirmation: bool = False
    high_risk_domain: bool = False
    risk_domain_tags: list[str] = Field(default_factory=list)


class PrimaryCard(FlexibleSchema):
    card_type: CardType
    common: dict[str, Any]
    specific: dict[str, Any]
    evidence_refs: list[str]
    action_entries: list[dict[str, Any]]
    display_name: str | None = None
    high_risk_domain: bool = False
    risk_domain_tags: list[str] = Field(default_factory=list)


class ReconstructionTask(FlexibleSchema):
    task_id: str
    video_asset_id: str
    session_context: SessionContext
    source_status: SourceStatus
    asset_status: AssetStatus
    retrieval_status: RetrievalStatus
    primary_card: PrimaryCard
    asset_kind: AssetKind | None = None
    demo_user_context_id: str | None = None
    related_assets: list[RelatedAsset] = Field(default_factory=list)
    inferences: list[InferenceItem] = Field(default_factory=list)
    generated_outputs: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


class CreateReconstructionTaskRequest(FlexibleSchema):
    source_id: str
    source_type: str | None = None
    session_context: SessionContext | None = None
    demo_user_context_id: str | None = None
    asset_kind: AssetKind | None = None


class SaveSnapshotRequest(FlexibleSchema):
    title: str | None = None
    user_note: str | None = None
