from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.main import app, create_app


def test_create_app_returns_fastapi_app_with_openapi_enabled():
    test_app = create_app(Settings(_env_file=None))
    client = TestClient(test_app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Content Matrix API"


def test_module_level_app_is_created_from_factory():
    assert app.title == "Content Matrix API"
    assert app.version == "0.0.1"


def test_health_returns_deterministic_mock_payload():
    test_app = create_app(Settings(_env_file=None))
    client = TestClient(test_app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "content-matrix",
        "version": "0.0.1",
        "mode": "mock",
    }


def test_health_reflects_settings_version_and_non_mock_provider():
    settings = Settings(_env_file=None, app_version="1.2.3", llm_mock_mode=False, llm_provider="openai")
    test_app = create_app(settings)
    client = TestClient(test_app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["version"] == "1.2.3"
    assert response.json()["mode"] == "openai"


def test_cors_uses_configured_origins_without_wildcard_credentials():
    allowed_origin = "https://frontend.example"
    settings = Settings(_env_file=None, allowed_origins=[allowed_origin])
    test_app = create_app(settings)
    client = TestClient(test_app)

    response = client.options(
        "/health",
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed_origin
    assert response.headers["access-control-allow-credentials"] == "true"
    assert response.headers["access-control-allow-origin"] != "*"


def test_api_v1_router_is_mounted_even_when_empty():
    settings = Settings(_env_file=None)
    test_app = create_app(settings)

    route_paths = {route.path for route in test_app.routes}

    assert settings.api_v1_prefix in route_paths
