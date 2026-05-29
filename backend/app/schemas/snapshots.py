from pydantic import Field

from backend.app.schemas.common import CardType, FlexibleSchema


class SavedReconstructionSnapshot(FlexibleSchema):
    snapshot_id: str
    source_asset_id: str
    source_task_id: str
    card_type: CardType
    title: str
    saved_summary: str
    key_decision_or_action: str | None = None
    evidence_refs: list[str]
    related_asset_refs: list[str] = Field(default_factory=list)
    saved_at: str
    user_note: str | None = None
    high_risk_domain: bool = False
    risk_domain_tags: list[str] = Field(default_factory=list)
