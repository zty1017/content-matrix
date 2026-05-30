from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.main import create_app
from backend.app.schemas import DemoUserAssetContext, VideoContentAsset


def build_client() -> TestClient:
    return TestClient(create_app(Settings(_env_file=None)))


def test_demo_contexts_list_returns_seeded_contexts_with_chinese_demo_copy():
    client = build_client()

    response = client.get("/api/v1/demo-contexts")

    assert response.status_code == 200
    contexts = [DemoUserAssetContext.model_validate(item) for item in response.json()]
    assert [context.demo_user_context_id for context in contexts] == [
        "ctx_efficiency_worker",
        "ctx_local_culture",
        "ctx_low_budget_student",
    ]
    assert contexts[0].display_name == "效率优先上班族资产上下文"
    assert contexts[0].context_summary == "历史资产偏向少排队、交通方便、预约制、短时间完成体验。"


def test_demo_context_detail_preserves_fixture_ids_and_summary():
    client = build_client()

    response = client.get("/api/v1/demo-contexts/ctx_low_budget_student")

    assert response.status_code == 200
    context = DemoUserAssetContext.model_validate(response.json())
    assert context.demo_user_context_id == "ctx_low_budget_student"
    assert context.display_name == "低预算学生资产上下文"
    assert context.asset_ids == [
        "asset_huaian_low_budget_daytrip",
        "asset_bus_accessible_foods",
        "asset_under_100_local_experience",
    ]
    assert "省钱" in context.context_summary


def test_asset_search_matches_query_and_tag_deterministically():
    client = build_client()

    response = client.get("/api/v1/assets/search", params={"query": "排队", "tag": "效率"})

    assert response.status_code == 200
    assets = [VideoContentAsset.model_validate(item) for item in response.json()]
    assert [asset.asset_id for asset in assets] == [
        "asset_reservation_offpeak_tips",
        "asset_weekend_queue_avoidance",
    ]
    assert all("效率" in asset.content_domain_tags for asset in assets)


def test_asset_search_supports_multiple_tags_without_ranking_logic():
    client = build_client()

    response = client.get("/api/v1/assets/search", params=[("tag", "淮安"), ("tag", "文化")])

    assert response.status_code == 200
    assert [item["asset_id"] for item in response.json()] == [
        "asset_huaian_cuisine_background",
    ]


def test_asset_search_finds_08_food_and_later_related_video():
    client = build_client()

    food_response = client.get("/api/v1/assets/search", params={"query": "重庆", "tag": "美食"})
    later_response = client.get("/api/v1/assets/search", params={"query": "后续", "tag": "重庆"})

    assert food_response.status_code == 200
    assert later_response.status_code == 200
    assert [item["asset_id"] for item in food_response.json()] == [
        "asset_douyin_08_chongqing_food_daydream",
    ]
    assert [item["asset_id"] for item in later_response.json()] == [
        "asset_douyin_07_chongqing_bbq_travel",
    ]


def test_empty_asset_search_returns_200_empty_list():
    client = build_client()

    response = client.get("/api/v1/assets/search", params={"query": "不存在的资产搜索词"})

    assert response.status_code == 200
    assert response.json() == []
