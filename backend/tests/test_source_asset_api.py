from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.main import create_app
from backend.app.schemas import VideoContentAsset


def build_client() -> TestClient:
    return TestClient(create_app(Settings(_env_file=None)))


def test_preset_source_resolves_from_fixture_mapping():
    client = build_client()

    response = client.post(
        "/api/v1/source/resolve",
        json={"source_type": "preset", "source_id": "preset_current_techu_huaian_hotel_candidate"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "resolved_source_id": "preset_current_techu_huaian_hotel_candidate",
        "source_type": "preset",
        "mapping_id": "mapping_demo_current_techu_huaian_hotel_candidate",
        "video_asset_id": "asset_current_techu_huaian_hotel_candidate",
        "task_id": "task_demo_p0a_low_budget_student",
        "demo_user_context_id": "ctx_low_budget_student",
        "title": "这条探店视频适合我周六下午去吗？",
        "resolution_strategy": "cache_matched",
    }


def test_douyin_like_source_validates_shape_and_maps_without_network():
    client = build_client()

    response = client.post(
        "/api/v1/source/resolve",
        json={
            "source_type": "douyin_url",
            "source_url": "https://v.douyin.com/preset_current_techu_huaian_hotel_candidate/",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_type"] == "douyin_url"
    assert payload["resolved_source_id"] == "preset_current_techu_huaian_hotel_candidate"
    assert payload["video_asset_id"] == "asset_current_techu_huaian_hotel_candidate"


def test_douyin_08_food_source_maps_to_local_demo_asset_without_network():
    client = build_client()

    response = client.post(
        "/api/v1/source/resolve",
        json={"source_type": "douyin_url", "source_url": "https://v.douyin.com/w3JLRkaZ6UQ/"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "resolved_source_id": "w3JLRkaZ6UQ",
        "source_type": "douyin_url",
        "mapping_id": "mapping_demo_douyin_08_chongqing_food",
        "video_asset_id": "asset_douyin_08_chongqing_food_daydream",
        "task_id": "task_demo_douyin_08_food_low_budget",
        "demo_user_context_id": "ctx_low_budget_student",
        "title": "昨晚做了个饿梦，梦到我又去雾都了",
        "resolution_strategy": "cache_matched",
    }


def test_huaian_douyin_alias_maps_to_existing_local_demo_task():
    client = build_client()

    response = client.post(
        "/api/v1/source/resolve",
        json={"source_type": "douyin_url", "source_url": "https://v.douyin.com/K5I9o0ITcJ8/"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["resolved_source_id"] == "K5I9o0ITcJ8"
    assert payload["video_asset_id"] == "asset_current_techu_huaian_hotel_candidate"
    assert payload["task_id"] == "task_demo_p0a_low_budget_student"


def test_upload_reference_source_maps_to_fixture_without_binary_upload():
    client = build_client()

    response = client.post(
        "/api/v1/source/resolve",
        json={
            "source_type": "upload_reference",
            "upload_reference_id": "mapping_demo_current_techu_huaian_hotel_candidate",
        },
    )

    assert response.status_code == 200
    assert response.json()["resolved_source_id"] == "mapping_demo_current_techu_huaian_hotel_candidate"
    assert response.json()["video_asset_id"] == "asset_current_techu_huaian_hotel_candidate"


def test_invalid_source_uses_domain_error_envelope():
    client = build_client()

    response = client.post(
        "/api/v1/source/resolve",
        json={"source_type": "douyin_url", "source_url": "https://example.com/not-douyin"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_source",
        "message": "Unsupported or unmapped source.",
        "detail": {
            "field": "source_url",
            "allowed": ["preset", "douyin_url", "upload_reference"],
        },
    }


def test_asset_build_returns_schema_valid_fixture_asset():
    client = build_client()

    response = client.post(
        "/api/v1/assets/build",
        json={"resolved_source_id": "preset_current_techu_huaian_hotel_candidate"},
    )

    assert response.status_code == 200
    payload = response.json()
    asset = VideoContentAsset.model_validate(payload["asset"])
    assert payload["asset_id"] == "asset_current_techu_huaian_hotel_candidate"
    assert payload["status"] == "asset_complete"
    assert payload["source_resolution"]["mapping_id"] == "mapping_demo_current_techu_huaian_hotel_candidate"
    assert asset.asset_id == payload["asset_id"]
    assert asset.source.mapping_id == "mapping_demo_current_techu_huaian_hotel_candidate"


def test_asset_get_returns_schema_valid_fixture_asset():
    client = build_client()

    response = client.get("/api/v1/assets/asset_current_techu_huaian_hotel_candidate")

    assert response.status_code == 200
    asset = VideoContentAsset.model_validate(response.json())
    assert asset.asset_id == "asset_current_techu_huaian_hotel_candidate"
    assert asset.source.title == "这条探店视频适合我周六下午去吗？"


def test_douyin_08_food_asset_get_returns_local_media_paths():
    client = build_client()

    response = client.get("/api/v1/assets/asset_douyin_08_chongqing_food_daydream")

    assert response.status_code == 200
    asset = VideoContentAsset.model_validate(response.json())
    assert asset.source.original_url == "https://v.douyin.com/w3JLRkaZ6UQ/"
    assert asset.source.local_path is not None
    assert "08-美食" in asset.source.local_path
    assert asset.source.cover_path is not None
    assert asset.demo_metadata["preferred_asr"] == "doubao-bigasr-flash"


def test_openapi_includes_source_resolve_examples():
    client = build_client()

    response = client.get("/openapi.json")


    assert response.status_code == 200
    examples = response.json()["paths"]["/api/v1/source/resolve"]["post"]["requestBody"]["content"][
        "application/json"
    ]["examples"]
    assert {"valid_preset", "valid_douyin_url", "invalid_source"}.issubset(examples)


def test_openapi_includes_examples_for_reviewed_v1_endpoints():
    client = build_client()

    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    source_resolve_200 = paths["/api/v1/source/resolve"]["post"]["responses"]["200"]["content"]["application/json"]
    asset_detail_200 = paths["/api/v1/assets/{asset_id}"]["get"]["responses"]["200"]["content"]["application/json"]
    task_detail_200 = paths["/api/v1/tasks/{task_id}"]["get"]["responses"]["200"]["content"]["application/json"]
    snapshots_200 = paths["/api/v1/snapshots"]["get"]["responses"]["200"]["content"]["application/json"]

    assert source_resolve_200["example"]["resolved_source_id"] == "preset_current_techu_huaian_hotel_candidate"
    assert asset_detail_200["example"]["asset_id"] == "asset_current_techu_huaian_hotel_candidate"
    assert task_detail_200["example"]["task_id"] == "task_runtime_preset_current_techu_huaian_hotel_candidate"
    assert "preset_resolution" in paths["/api/v1/assets/build"]["post"]["requestBody"]["content"]["application/json"]["examples"]
    assert "example" in paths["/api/v1/assets/build"]["post"]["responses"]["200"]["content"]["application/json"]
    assert "example" in paths["/api/v1/assets/search"]["get"]["responses"]["200"]["content"]["application/json"]
    assert "example" in paths["/api/v1/demo-contexts"]["get"]["responses"]["200"]["content"]["application/json"]
    assert "from_resolved_preset" in paths["/api/v1/tasks"]["post"]["requestBody"]["content"]["application/json"]["examples"]
    assert "example" in paths["/api/v1/tasks"]["post"]["responses"]["200"]["content"]["application/json"]
    assert "example" in paths["/api/v1/tasks/{task_id}/generate-card"]["post"]["responses"]["200"]["content"]["application/json"]
    assert "weekend_candidate" in paths["/api/v1/tasks/{task_id}/save-snapshot"]["post"]["requestBody"]["content"]["application/json"]["examples"]
    assert "example" in paths["/api/v1/tasks/{task_id}/save-snapshot"]["post"]["responses"]["200"]["content"]["application/json"]
    assert snapshots_200["example"][0]["snapshot_id"] == "snap_demo_p0a_low_budget_student"
