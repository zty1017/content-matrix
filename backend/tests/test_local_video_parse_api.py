from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.main import create_app
from backend.app.schemas.local_video import LocalVideoParseResult
from backend.app.services.local_video_parser import LocalVideoParser
from backend.app.api.v1.local_video import get_local_video_parser


def build_client(settings: Settings | None = None) -> TestClient:
    return TestClient(create_app(settings or Settings(_env_file=None)))


def test_local_video_parse_returns_fallback_asset_without_network():
    client = build_client()

    response = client.post(
        "/api/v1/local-video/parse",
        json={"local_reference_id": "demo_unparsed_workplace_06", "parse_mode": "fallback"},
    )

    assert response.status_code == 200
    result = LocalVideoParseResult.model_validate(response.json())
    assert result.local_reference_id == "demo_unparsed_workplace_06"
    assert result.content_type == "workplace_skit"
    assert result.asset.asset_id == "asset_runtime_demo_unparsed_workplace_06"
    assert result.asset.reconstruction_type == "experience"
    assert result.asr.provider == "local-hardcoded-fallback"
    assert result.asr.is_fallback is True
    assert result.asr.detail["network_call"] == "not_performed"
    assert [block["type"] for block in result.display_blocks] == [
        "plot_structure",
        "brand_placement",
        "remix_hooks",
    ]
    assert "06-职场" in result.asset.source.local_path


def test_local_video_parse_doubao_mode_keeps_deterministic_fallback_when_configured():
    settings = Settings(
        _env_file=None,
        asr_provider="doubao_flash",
        asr_mock_mode=False,
        doubao_api_key="test-doubao-key",
    )
    app = create_app(settings)
    app.dependency_overrides[get_local_video_parser] = lambda: LocalVideoParser(settings)
    client = TestClient(app)

    response = client.post(
        "/api/v1/local-video/parse",
        json={"local_reference_id": "demo_unparsed_workplace_06", "parse_mode": "doubao_if_configured"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["asr"]["provider"] == "doubao-bigasr-flash"
    assert result["asr"]["is_fallback"] is True
    assert result["asr"]["detail"]["network_call"] == "not_performed_in_demo"
    assert result["asr"]["detail"]["future_provider"] == "volc.bigasr.auc_turbo"


def test_local_video_parse_rejects_unknown_reference_with_domain_error():
    client = build_client()

    response = client.post(
        "/api/v1/local-video/parse",
        json={"local_reference_id": "missing_video", "parse_mode": "fallback"},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert response.json()["detail"]["resource"] == "local_video_reference"
    assert "demo_unparsed_workplace_06" in response.json()["detail"]["available_reference_ids"]


def test_local_video_parse_rejects_invalid_parse_mode_with_fastapi_validation():
    client = build_client()

    response = client.post(
        "/api/v1/local-video/parse",
        json={"local_reference_id": "demo_unparsed_workplace_06", "parse_mode": "real_network"},
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_local_video_parse_finance_candidate_returns_knowledge_display_blocks():
    client = build_client()

    response = client.post(
        "/api/v1/local-video/parse",
        json={"local_reference_id": "demo_unparsed_finance_12", "parse_mode": "fallback"},
    )

    assert response.status_code == 200
    result = LocalVideoParseResult.model_validate(response.json())
    assert result.content_type == "finance_analysis"
    assert result.asset.reconstruction_type == "knowledge"
    assert "12-财经" in result.asset.source.local_path
    assert [block["type"] for block in result.display_blocks] == [
        "viewpoint_summary",
        "risk_notice",
        "verification_checklist",
    ]


def test_openapi_includes_local_video_parse_examples():
    client = build_client()

    response = client.get("/openapi.json")

    assert response.status_code == 200
    examples = response.json()["paths"]["/api/v1/local-video/parse"]["post"]["requestBody"]["content"][
        "application/json"
    ]["examples"]
    assert {"unparsed_finance_fallback", "doubao_boundary_with_fallback"}.issubset(examples)
