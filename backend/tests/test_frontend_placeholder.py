from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
README_PATH = FRONTEND_DIR / "README.md"


@pytest.fixture
def readme_text() -> str:
    assert README_PATH.exists(), f"frontend README must exist at {README_PATH}"
    return README_PATH.read_text(encoding="utf-8")


def test_frontend_readme_exists(readme_text: str) -> None:
    assert "前端" in readme_text, "README should be Chinese and mention frontend"


def test_readme_mentions_backend_contract_sources(readme_text: str) -> None:
    required_mentions = [
        "docs/setup.md",
        "docs/api-contract.md",
        "docs/",
        "/openapi.json",
        "http://localhost:8000",
    ]
    for item in required_mentions:
        assert item in readme_text, f"README must mention {item}"


def test_readme_mentions_allowed_local_origins(readme_text: str) -> None:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    for origin in origins:
        assert origin in readme_text, f"README must mention allowed origin {origin}"


def test_no_frontend_package_json() -> None:
    assert not (FRONTEND_DIR / "package.json").exists(), "No frontend package.json should exist in v0"


def test_no_frontend_src_directory() -> None:
    assert not (FRONTEND_DIR / "src").exists(), "No frontend src/ directory should exist in v0"


def test_no_frontend_build_configs() -> None:
    forbidden = [
        "vite.config.ts",
        "vite.config.js",
        "vite.config.mjs",
        "next.config.js",
        "next.config.ts",
        "vue.config.js",
        "tsconfig.json",
        "tailwind.config.js",
        "webpack.config.js",
        "rollup.config.js",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lockb",
    ]
    for name in forbidden:
        assert not (FRONTEND_DIR / name).exists(), f"No {name} should exist in frontend/ in v0"
