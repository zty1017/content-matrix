import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.core.errors import ConstrainedRequestError, FixtureDataError, InvalidSourceError, NotFoundError
from backend.app.main import create_app
from backend.app.repositories import JsonFixtureRepository
from backend.app.services.source_resolver import SourceResolver


def build_client() -> TestClient:
    app = create_app(Settings(_env_file=None))

    @app.get("/test/not-found")
    def raise_not_found() -> None:
        raise NotFoundError("Requested asset was not found.", {"resource": "video_content_asset", "identifier": "asset_missing"})

    @app.get("/test/invalid-source")
    def raise_invalid_source() -> None:
        raise InvalidSourceError(
            "Unsupported source type.",
            {
                "field": "source.type",
                "allowed": ["douyin_link", "local_mapping", "preset_video", "upload_video", "upload_audio", "text_only", "demo_seed"],
            },
        )

    @app.get("/test/constrained-request")
    def raise_constrained_request() -> None:
        raise ConstrainedRequestError(
            "Request is constrained by the current high-risk policy.",
            {"high_risk_domain": True, "risk_domain_tags": ["local_service_decision"]},
        )

    @app.get("/test/fixture-data-failure")
    def raise_fixture_data_failure() -> None:
        raise FixtureDataError(
            "Fixture data could not be loaded.",
            {"fixture": "seed_video_content_assets", "dataset": "content-matrix-v0"},
        )

    @app.get("/test/validation/{item_id}")
    def validation_route(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    return TestClient(app)


def assert_error_response(response, *, status_code: int, code: str, message: str, detail: dict | None) -> None:
    assert response.status_code == status_code
    assert response.json() == {"code": code, "message": message, "detail": detail}


def test_not_found_uses_top_level_error_envelope():
    client = build_client()

    response = client.get("/test/not-found")

    assert_error_response(
        response,
        status_code=404,
        code="not_found",
        message="Requested asset was not found.",
        detail={"resource": "video_content_asset", "identifier": "asset_missing"},
    )


def test_invalid_source_uses_top_level_error_envelope():
    client = build_client()

    response = client.get("/test/invalid-source")

    assert_error_response(
        response,
        status_code=400,
        code="invalid_source",
        message="Unsupported source type.",
        detail={
            "field": "source.type",
            "allowed": ["douyin_link", "local_mapping", "preset_video", "upload_video", "upload_audio", "text_only", "demo_seed"],
        },
    )


def test_constrained_request_uses_top_level_error_envelope():
    client = build_client()

    response = client.get("/test/constrained-request")

    assert_error_response(
        response,
        status_code=422,
        code="constrained_request",
        message="Request is constrained by the current high-risk policy.",
        detail={"high_risk_domain": True, "risk_domain_tags": ["local_service_decision"]},
    )


def test_fixture_data_failure_uses_top_level_error_envelope_without_secret_leakage():
    client = build_client()

    response = client.get("/test/fixture-data-failure")

    assert_error_response(
        response,
        status_code=500,
        code="fixture_data_failure",
        message="Fixture data could not be loaded.",
        detail={"fixture": "seed_video_content_assets", "dataset": "content-matrix-v0"},
    )
    assert "Traceback" not in response.text
    assert "super-secret" not in response.text


def test_fastapi_validation_errors_keep_default_shape():
    client = build_client()

    response = client.get("/test/validation/not-an-int")

    assert response.status_code == 422
    assert "code" not in response.json()
    assert "message" not in response.json()
    assert "detail" in response.json()
    assert isinstance(response.json()["detail"], list)


def test_fixture_repository_load_failure_on_api_path_uses_domain_error_envelope(tmp_path: Path):
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()
    (fixtures_dir / "source_mappings.json").write_text("not-json", encoding="utf-8")
    repository = JsonFixtureRepository(fixtures_dir=fixtures_dir, runtime_dir=tmp_path / "runtime")
    app = create_app(Settings(_env_file=None))

    @app.get("/test/repository-load-failure")
    def repository_load_failure() -> dict:
        SourceResolver(repository).resolve(
            source_type="preset",
            source_id="preset_current_techu_huaian_hotel_candidate",
        )
        return {}

    response = TestClient(app).get("/test/repository-load-failure")

    assert response.status_code == 500
    payload = response.json()
    assert payload["code"] == "fixture_data_failure"
    assert payload["message"] == "Fixture data could not be loaded."
    assert "Malformed JSON data file" in payload["detail"]["reason"]
    assert "Traceback" not in response.text


def test_openapi_error_schema_matches_top_level_domain_envelope():
    client = build_client()

    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()["components"]["schemas"]["ApiErrorResponse"]
    assert {"code", "message"}.issubset(schema["required"])
    assert "error" not in schema["properties"]
