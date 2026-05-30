from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.api.v1.cube import get_cube_view_service
from backend.app.api.v1.tasks import get_reconstruction_generator, get_task_state_service
from backend.app.core.config import Settings
from backend.app.main import create_app
from backend.app.repositories import JsonFixtureRepository
from backend.app.services.cube_view import CubeViewService
from backend.app.services.reconstruction_generator import ReconstructionGenerator
from backend.app.services.task_state import TaskStateService


def build_client(tmp_path: Path) -> TestClient:
    repository = JsonFixtureRepository(runtime_dir=tmp_path / "runtime")
    task_service = TaskStateService(repository)
    generator = ReconstructionGenerator(repository)
    cube_service = CubeViewService(repository)
    app = create_app(Settings(_env_file=None))
    app.dependency_overrides[get_task_state_service] = lambda: task_service
    app.dependency_overrides[get_reconstruction_generator] = lambda: generator
    app.dependency_overrides[get_cube_view_service] = lambda: cube_service
    return TestClient(app)


def test_cube_view_projects_fixture_task_to_six_clickable_faces(tmp_path: Path):
    client = build_client(tmp_path)

    response = client.get("/api/v1/cube/tasks/task_demo_douyin_08_food_low_budget")

    assert response.status_code == 200
    payload = response.json()
    assert payload["task_id"] == "task_demo_douyin_08_food_low_budget"
    assert payload["cube_state"] == "ready"
    assert payload["animation_phase"] == "final_form"
    assert payload["progress"]["percent"] == 100.0
    assert payload["progress"]["message"] == "内容魔方已完成，可以点击各面查看重构结果。"
    assert [face["face_id"] for face in payload["faces"]] == [
        "source",
        "primary_card",
        "related_assets",
        "inferences",
        "evidence",
        "snapshot",
    ]
    assert payload["faces"][1]["target_ref"] == {"type": "task", "id": "task_demo_douyin_08_food_low_budget"}
    assert payload["faces"][5]["action"]["href"] == "/api/v1/tasks/task_demo_douyin_08_food_low_budget/save-snapshot"


def test_cube_view_tracks_runtime_task_before_and_after_generation(tmp_path: Path):
    client = build_client(tmp_path)
    create_response = client.post(
        "/api/v1/tasks",
        json={"source_id": "preset_current_techu_huaian_hotel_candidate", "source_type": "preset"},
    )
    task_id = create_response.json()["task_id"]

    before_response = client.get(f"/api/v1/cube/tasks/{task_id}")

    assert before_response.status_code == 200
    before = before_response.json()
    assert before["cube_state"] == "transforming"
    assert before["animation_phase"] == "matrix_linking"
    assert before["progress"]["percent"] == 70.0
    assert before["progress"]["steps"][2]["status"] == "ready"
    assert before["progress"]["steps"][3]["status"] == "pending"
    assert before["faces"][5]["status"] == "disabled"
    assert before["warnings"]

    generate_response = client.post(f"/api/v1/tasks/{task_id}/generate-card")
    assert generate_response.status_code == 200

    after_response = client.get(f"/api/v1/cube/tasks/{task_id}")
    after = after_response.json()
    assert after["cube_state"] == "ready"
    assert after["animation_phase"] == "final_form"
    assert after["progress"]["percent"] == 100.0
    assert after["faces"][5]["status"] == "ready"


def test_cube_progress_endpoint_returns_fixture_derived_demo_progress(tmp_path: Path):
    client = build_client(tmp_path)
    create_response = client.post(
        "/api/v1/tasks",
        json={"source_id": "preset_current_techu_huaian_hotel_candidate", "source_type": "preset"},
    )
    task_id = create_response.json()["task_id"]

    response = client.get(f"/api/v1/cube/tasks/{task_id}/progress")

    assert response.status_code == 200
    payload = response.json()
    assert payload["task_id"] == task_id
    assert payload["cube_state"] == "transforming"
    assert payload["animation_phase"] == "matrix_linking"
    assert payload["percent"] == 70.0
    assert payload["message"] == "正在关联历史资产与证据链，组装魔方面。"
    assert [step["step_id"] for step in payload["steps"]] == [
        "source_resolution",
        "content_reconstruction",
        "matrix_linking",
        "final_form",
    ]


def test_cube_view_missing_task_uses_domain_error(tmp_path: Path):
    client = build_client(tmp_path)

    response = client.get("/api/v1/cube/tasks/task_missing")

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "Reconstruction task was not found.",
        "detail": {"resource": "reconstruction_task", "identifier": "task_missing"},
    }


def test_cube_progress_missing_task_uses_domain_error(tmp_path: Path):
    client = build_client(tmp_path)

    response = client.get("/api/v1/cube/tasks/task_missing/progress")

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "Reconstruction task was not found.",
        "detail": {"resource": "reconstruction_task", "identifier": "task_missing"},
    }


def test_openapi_includes_cube_view_route(tmp_path: Path):
    client = build_client(tmp_path)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/cube/tasks/{task_id}" in response.json()["paths"]
    assert "/api/v1/cube/tasks/{task_id}/progress" in response.json()["paths"]
