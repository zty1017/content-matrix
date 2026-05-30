from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
REQUIRED_DOCS = [
    "README.md",
    "setup.md",
    "architecture.md",
    "api-contract.md",
    "domain-model.md",
    "mock-data.md",
    "v0-scope-and-exclusions.md",
]

REQUIRED_ENDPOINTS = [
    "/health",
    "/api/v1/source/resolve",
    "/api/v1/assets/build",
    "/api/v1/assets/{asset_id}",
    "/api/v1/assets/search",
    "/api/v1/demo-contexts",
    "/api/v1/demo-contexts/{context_id}",
    "/api/v1/tasks",
    "/api/v1/tasks/{task_id}",
    "/api/v1/tasks/{task_id}/generate-card",
    "/api/v1/tasks/{task_id}/save-snapshot",
    "/api/v1/snapshots",
    "/api/v1/local-video/parse",
    "/api/v1/cube/tasks/{task_id}",
    "/api/v1/cube/tasks/{task_id}/progress",
]


def _read_doc(filename: str) -> str:
    path = DOCS_DIR / filename
    assert path.exists(), f"Missing required doc: {filename}"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("filename", REQUIRED_DOCS)
def test_required_doc_exists(filename: str):
    assert (DOCS_DIR / filename).exists()


def test_readme_contains_project_overview_and_doc_links():
    content = _read_doc("README.md")
    assert "Content Matrix" in content
    assert "setup.md" in content
    assert "api-contract.md" in content
    assert "Swagger UI" in content or "openapi.json" in content
    assert "mock" in content.lower()


def test_setup_describes_uv_commands():
    content = _read_doc("setup.md")
    assert "uv" in content
    assert "uv run uvicorn" in content
    assert "uv run pytest" in content
    assert "uv pip install" in content
    assert ".env" in content
    assert "localhost:8000" in content or "8000" in content


def test_architecture_describes_backend_layers():
    content = _read_doc("architecture.md")
    assert "create_app" in content
    assert "JsonFixtureRepository" in content
    assert "DomainError" in content
    assert "fixtures/" in content
    assert "runtime/" in content
    assert "依赖注入" in content or "Depends" in content


def test_api_contract_lists_all_implemented_endpoints():
    content = _read_doc("api-contract.md")
    for endpoint in REQUIRED_ENDPOINTS:
        assert endpoint in content, f"Endpoint {endpoint} not found in api-contract.md"


def test_api_contract_documents_error_envelope():
    content = _read_doc("api-contract.md")
    assert '"code"' in content
    assert '"message"' in content
    assert '"detail"' in content
    assert "FastAPI" in content and "422" in content
    assert "默认的 FastAPI 422" in content or "default" in content.lower()


def test_api_contract_documents_domain_error_codes():
    content = _read_doc("api-contract.md")
    assert "not_found" in content
    assert "invalid_source" in content
    assert "constrained_request" in content
    assert "fixture_data_failure" in content


def test_domain_model_describes_key_schemas():
    content = _read_doc("domain-model.md")
    assert "VideoContentAsset" in content
    assert "ReconstructionTask" in content
    assert "PrimaryCard" in content
    assert "SavedReconstructionSnapshot" in content
    assert "EvidenceItem" in content
    assert "SessionContext" in content
    assert "ConfidenceLevel" in content


def test_mock_data_documents_fixture_and_runtime():
    content = _read_doc("mock-data.md")
    assert "fixtures/" in content
    assert "runtime/" in content
    assert "source_mappings.json" in content
    assert "video_content_assets.json" in content
    assert "reconstruction_tasks.json" in content
    assert "demo_user_asset_contexts.json" in content
    assert "saved_reconstruction_snapshots.json" in content
    assert "FixtureRepositoryError" in content or "fixture" in content.lower()


def test_v0_scope_explicitly_excludes_real_capabilities():
    content = _read_doc("v0-scope-and-exclusions.md")
    assert "真实抖音解析" in content or "real Douyin" in content or "douyin" in content.lower()
    assert "真实 LLM" in content or "real LLM" in content or "llm" in content.lower()
    assert "数据库" in content or "database" in content.lower()
    assert "前端 UI" in content or "frontend UI" in content or "前端" in content
    assert "部署" in content or "deployment" in content.lower()


def test_docs_are_primarily_chinese():
    """Verify that docs contain significant Chinese characters."""
    for filename in REQUIRED_DOCS:
        content = _read_doc(filename)
        chinese_chars = [c for c in content if "\u4e00" <= c <= "\u9fff"]
        assert len(chinese_chars) > 50, f"{filename} appears to lack sufficient Chinese prose"
