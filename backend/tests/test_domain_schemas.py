import json
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.app.schemas import (
    ApiErrorResponse,
    DraftVideoContentAsset,
    EvidenceItem,
    InferenceItem,
    PrimaryCard,
    ReconstructionTask,
    SavedReconstructionSnapshot,
    VideoContentAsset,
)
from backend.app.schemas.demo_contexts import DemoSeedAssetBundle, DemoUserAssetContext


REFERENCE_ROOT = Path(__file__).resolve().parents[3] / "onlinechatcontext"


def load_reference_json(relative_path: str) -> dict:
    return json.loads((REFERENCE_ROOT / relative_path).read_text(encoding="utf-8"))


def test_sample_reconstruction_task_validates_without_field_renaming():
    payload = load_reference_json("samples/sample_reconstruction_task_p0a.json")

    task = ReconstructionTask.model_validate(payload)
    dumped = task.model_dump(mode="json")

    assert dumped["task_id"] == payload["task_id"]
    assert dumped["source_status"] == payload["source_status"]
    assert dumped["asset_status"] == payload["asset_status"]
    assert dumped["retrieval_status"] == payload["retrieval_status"]
    assert dumped["primary_card"]["card_type"] == "decision"
    assert dumped["related_assets"][0]["influence_type"] == "preference_adaptation"
    assert isinstance(task.primary_card, PrimaryCard)
    assert isinstance(task.inferences[0], InferenceItem)


def test_demo_seed_asset_bundle_validates_all_seed_assets_and_contexts():
    payload = load_reference_json("samples/p0a_demo_seed_assets.json")

    bundle = DemoSeedAssetBundle.model_validate(payload)
    dumped = bundle.model_dump(mode="json")

    assert len(bundle.demo_user_contexts) == 3
    assert len(bundle.seed_video_content_assets) == 9
    assert dumped["demo_user_contexts"][0]["demo_user_context_id"] == "ctx_low_budget_student"
    assert dumped["seed_video_content_assets"][0]["source"]["type"] == "demo_seed"
    assert isinstance(bundle.demo_user_contexts[0], DemoUserAssetContext)
    assert isinstance(bundle.seed_video_content_assets[0], VideoContentAsset)
    assert isinstance(bundle.seed_video_content_assets[0].evidence[0], EvidenceItem)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("source_status", "done"),
        ("asset_status", "ready"),
        ("retrieval_status", "matched"),
    ],
)
def test_reconstruction_task_rejects_invalid_state_enums(field: str, bad_value: str):
    payload = load_reference_json("samples/sample_reconstruction_task_p0a.json")
    payload[field] = bad_value

    with pytest.raises(ValidationError):
        ReconstructionTask.model_validate(payload)


def test_video_content_asset_rejects_invalid_source_and_confidence_enums():
    payload = load_reference_json("samples/p0a_demo_seed_assets.json")["seed_video_content_assets"][0]
    payload = deepcopy(payload)
    payload["source"]["type"] = "webpage"
    payload["confidence_level"] = "certain"

    with pytest.raises(ValidationError):
        VideoContentAsset.model_validate(payload)


def test_draft_video_content_asset_enforces_draft_contract():
    payload = load_reference_json("samples/p0a_demo_seed_assets.json")["seed_video_content_assets"][0]
    draft_payload = deepcopy(payload)
    draft_payload.update(
        {
            "asset_id": "draft_asset_low_confidence",
            "is_draft": True,
            "confidence_level": "medium",
            "needs_confirmation": True,
            "upgrade_conditions": ["confirm source price", "confirm queue time"],
            "high_risk_domain": True,
            "risk_domain_tags": ["local_service_decision"],
        }
    )

    draft = DraftVideoContentAsset.model_validate(draft_payload)

    assert draft.is_draft is True
    assert draft.needs_confirmation is True
    assert draft.high_risk_domain is True
    assert draft.risk_domain_tags == ["local_service_decision"]

    invalid_payload = deepcopy(draft_payload)
    invalid_payload["confidence_level"] = "high"
    with pytest.raises(ValidationError):
        DraftVideoContentAsset.model_validate(invalid_payload)


def test_snapshot_and_error_envelope_models_are_json_ready():
    snapshot = SavedReconstructionSnapshot.model_validate(
        {
            "snapshot_id": "snap_demo_1",
            "source_asset_id": "asset_current_techu_huaian_hotel_candidate",
            "source_task_id": "task_demo_p0a_low_budget_student",
            "card_type": "decision",
            "title": "周末探店备选",
            "saved_summary": "价格和排队情况待确认后再决定。",
            "key_decision_or_action": "确认人均与排队情况",
            "evidence_refs": ["asset_huaian_low_budget_daytrip_ev1"],
            "related_asset_refs": ["asset_huaian_low_budget_daytrip"],
            "saved_at": "2026-05-30T00:00:00Z",
            "user_note": "适合预算内备选",
        }
    )
    error = ApiErrorResponse.model_validate(
        {
            "code": "invalid_state",
            "message": "Unsupported source_status value.",
            "detail": {"field": "source_status", "allowed": ["received"]},
        }
    )

    assert snapshot.model_dump(mode="json")["card_type"] == "decision"
    assert error.model_dump(mode="json") == {
        "code": "invalid_state",
        "message": "Unsupported source_status value.",
        "detail": {"field": "source_status", "allowed": ["received"]},
    }
