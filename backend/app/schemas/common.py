from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class FlexibleSchema(BaseModel):
    model_config = ConfigDict(extra="allow")


class ConfidenceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ReconstructionType(str, Enum):
    knowledge = "knowledge"
    procedure = "procedure"
    decision = "decision"
    experience = "experience"


class CardType(str, Enum):
    knowledge = "knowledge"
    procedure = "procedure"
    decision = "decision"


class SourceStatus(str, Enum):
    received = "received"
    cache_matched = "cache_matched"
    online_resolving = "online_resolving"
    file_processing = "file_processing"
    source_ready = "source_ready"
    source_partial = "source_partial"
    source_failed = "source_failed"
    fallback_selected = "fallback_selected"


class AssetStatus(str, Enum):
    asset_pending = "asset_pending"
    basic_generating = "basic_generating"
    basic_ready = "basic_ready"
    card_generating = "card_generating"
    card_ready = "card_ready"
    evidence_linking = "evidence_linking"
    asset_complete = "asset_complete"
    asset_failed = "asset_failed"


class RetrievalStatus(str, Enum):
    retrieval_pending = "retrieval_pending"
    retrieval_running = "retrieval_running"
    retrieval_empty = "retrieval_empty"
    retrieval_matched = "retrieval_matched"
    retrieval_applying = "retrieval_applying"
    retrieval_applied = "retrieval_applied"
    retrieval_failed = "retrieval_failed"


Metadata = dict[str, Any]
