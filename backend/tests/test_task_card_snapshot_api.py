import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.api.v1.tasks import get_reconstruction_generator, get_snapshot_service, get_task_state_service
from backend.app.core.config import Settings
from backend.app.main import create_app
from backend.app.repositories import JsonFixtureRepository
from backend.app.services.reconstruction_generator import ReconstructionGenerator
from backend.app.services.snapshot_service import SnapshotService
from backend.app.services.task_state import TaskStateService


def build_client(tmp_path: Path) -> tuple[TestClient, Path]:
    runtime_dir = tmp_path / "runtime"
    repository = JsonFixtureRepository(runtime_dir=runtime_dir)
    task_service = TaskStateService(repository)
    generator = ReconstructionGenerator(repository)
    snapshot_service = SnapshotService(repository)
    app = create_app(Settings(_env_file=None))
    app.dependency_overrides[get_task_state_service] = lambda: task_service
    app.dependency_overrides[get_reconstruction_generator] = lambda: generator
    app.dependency_overrides[get_snapshot_service] = lambda: snapshot_service
    return TestClient(app), runtime_dir


def test_create_status_generate_card_and_save_snapshot_flow_is_runtime_backed(tmp_path: Path):
    client, runtime_dir = build_client(tmp_path)

    create_response = client.post(
        "/api/v1/tasks",
        json={
            "source_id": "preset_current_techu_huaian_hotel_candidate",
            "source_type": "preset",
            "session_context": {
                "raw_text": "周六下午 2 小时，预算 100 元以内，不想排队。",
                "goals": ["短时间体验本地特色"],
                "constraints": ["2 小时以内", "预算 100 元以内"],
                "preferences": ["少排队"],
                "scenario": "本地生活/探店决策",
            },
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["task_id"] == "task_runtime_preset_current_techu_huaian_hotel_candidate"
    assert created["source_status"] == "cache_matched"
    assert created["asset_status"] == "basic_ready"
    assert created["retrieval_status"] == "retrieval_matched"
    assert (runtime_dir / "reconstruction_tasks.json").exists()

    status_response = client.get(f"/api/v1/tasks/{created['task_id']}")

    assert status_response.status_code == 200
    assert status_response.json()["session_context"]["raw_text"] == "周六下午 2 小时，预算 100 元以内，不想排队。"

    card_response = client.post(f"/api/v1/tasks/{created['task_id']}/generate-card")

    assert card_response.status_code == 200
    generated = card_response.json()
    assert generated["asset_status"] == "asset_complete"
    assert generated["retrieval_status"] == "retrieval_applied"
    assert generated["generated_outputs"] == [
        {
            "output_id": "out_task_runtime_preset_current_techu_huaian_hotel_candidate_primary_card",
            "type": "primary_card",
            "status": "ready",
        }
    ]

    snapshot_response = client.post(
        f"/api/v1/tasks/{created['task_id']}/save-snapshot",
        json={"user_note": "保留为周末备选", "title": "周末探店备选"},
    )

    assert snapshot_response.status_code == 200
    snapshot = snapshot_response.json()
    assert snapshot == {
        "snapshot_id": "snap_task_runtime_preset_current_techu_huaian_hotel_candidate",
        "source_asset_id": "asset_current_techu_huaian_hotel_candidate",
        "source_task_id": "task_runtime_preset_current_techu_huaian_hotel_candidate",
        "card_type": "decision",
        "title": "周末探店备选",
        "saved_summary": "基于当前视频事实、你的本次预算与历史低预算资产，系统生成有条件判断。",
        "key_decision_or_action": "确认人均与排队情况",
        "evidence_refs": ["asset_huaian_low_budget_daytrip_ev1"],
        "related_asset_refs": ["asset_huaian_low_budget_daytrip"],
        "saved_at": "2026-05-30T00:00:00Z",
        "user_note": "保留为周末备选",
        "high_risk_domain": False,
        "risk_domain_tags": [],
    }
    assert (runtime_dir / "saved_reconstruction_snapshots.json").exists()

    persisted_snapshots = json.loads((runtime_dir / "saved_reconstruction_snapshots.json").read_text(encoding="utf-8"))
    assert persisted_snapshots[0]["snapshot_id"] == "snap_task_runtime_preset_current_techu_huaian_hotel_candidate"


def test_missing_task_uses_domain_error_envelope(tmp_path: Path):
    client, _ = build_client(tmp_path)

    response = client.get("/api/v1/tasks/task_missing")

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "Reconstruction task was not found.",
        "detail": {"resource": "reconstruction_task", "identifier": "task_missing"},
    }


def test_generate_card_rejects_incomplete_draft_task_with_domain_error(tmp_path: Path):
    client, _ = build_client(tmp_path)
    create_response = client.post(
        "/api/v1/tasks",
        json={
            "source_id": "preset_current_techu_huaian_hotel_candidate",
            "source_type": "preset",
            "asset_kind": "draft",
        },
    )
    task_id = create_response.json()["task_id"]

    response = client.post(f"/api/v1/tasks/{task_id}/generate-card")

    assert response.status_code == 422
    assert response.json() == {
        "code": "constrained_request",
        "message": "Draft task must be completed before card generation.",
        "detail": {"task_id": task_id, "asset_kind": "draft", "missing": ["confirmed_source_facts"]},
    }


def test_generate_card_rejects_high_risk_task_with_domain_error(tmp_path: Path):
    client, _ = build_client(tmp_path)
    create_response = client.post(
        "/api/v1/tasks",
        json={
            "source_id": "preset_current_techu_huaian_hotel_candidate",
            "source_type": "preset",
            "session_context": {
                "raw_text": "帮我判断高风险事项。",
                "high_risk_domain": True,
                "risk_domain_tags": ["local_service_decision"],
            },
        },
    )
    task_id = create_response.json()["task_id"]

    response = client.post(f"/api/v1/tasks/{task_id}/generate-card")
    assert response.status_code == 422
    assert response.json() == {
        "code": "constrained_request",
        "message": "High-risk tasks require user confirmation before card generation.",
        "detail": {
            "task_id": task_id,
            "high_risk_domain": True,
            "risk_domain_tags": ["local_service_decision"],
        },
    }


def test_source_resolve_output_can_create_task_without_source_type_mismatch(tmp_path: Path):
    client, _ = build_client(tmp_path)

    resolve_response = client.post(
        "/api/v1/source/resolve",
        json={"source_type": "preset", "source_id": "preset_current_techu_huaian_hotel_candidate"},
    )
    assert resolve_response.status_code == 200

    create_response = client.post(
        "/api/v1/tasks",
        json={
            "source_id": resolve_response.json()["resolved_source_id"],
            "source_type": resolve_response.json()["source_type"],
        },
    )

    assert create_response.status_code == 200
    assert create_response.json()["task_id"] == "task_runtime_preset_current_techu_huaian_hotel_candidate"


def test_repeated_task_creation_uses_distinct_runtime_task_ids(tmp_path: Path):
    client, runtime_dir = build_client(tmp_path)
    payload = {"source_id": "preset_current_techu_huaian_hotel_candidate", "source_type": "preset"}

    first = client.post("/api/v1/tasks", json=payload)
    second = client.post("/api/v1/tasks", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["task_id"] == "task_runtime_preset_current_techu_huaian_hotel_candidate"
    assert second.json()["task_id"] == "task_runtime_preset_current_techu_huaian_hotel_candidate_2"
    persisted = json.loads((runtime_dir / "reconstruction_tasks.json").read_text(encoding="utf-8"))
    assert [item["task_id"] for item in persisted] == [
        "task_runtime_preset_current_techu_huaian_hotel_candidate",
        "task_runtime_preset_current_techu_huaian_hotel_candidate_2",
    ]


def test_task_create_rejects_fixture_source_type_name_in_public_contract(tmp_path: Path):
    client, _ = build_client(tmp_path)

    response = client.post(
        "/api/v1/tasks",
        json={
            "source_id": "preset_current_techu_huaian_hotel_candidate",
            "source_type": "preset_video",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_source",
        "message": "Source type does not match the configured mapping.",
        "detail": {"field": "source_type", "expected": "preset", "received": "preset_video"},
    }
