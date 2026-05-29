from pathlib import Path

from backend.app.core.config import Settings, get_settings


ENV_KEYS = {
    "APP_NAME",
    "APP_VERSION",
    "ENVIRONMENT",
    "DEBUG",
    "API_V1_PREFIX",
    "ALLOWED_ORIGINS",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "LLM_MOCK_MODE",
    "OPENAI_API_KEY",
    "DOUBAO_API_KEY",
    "DEEPSEEK_API_KEY",
    "QWEN_API_KEY",
    "MOCK_RESPONSE_DELAY_MS",
}


def clear_settings_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    get_settings.cache_clear()


def test_settings_default_to_offline_mock_mode(monkeypatch):
    clear_settings_env(monkeypatch)

    settings = Settings(_env_file=None)

    assert settings.app_name == "Content Matrix"
    assert settings.app_version == "0.0.1"
    assert settings.environment == "local"
    assert settings.debug is False
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.allowed_origins == [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    assert settings.llm_provider == "mock"
    assert settings.llm_model == "mock-content-matrix-v0"
    assert settings.llm_mock_mode is True
    assert settings.openai_api_key is None
    assert settings.doubao_api_key is None
    assert settings.deepseek_api_key is None
    assert settings.qwen_api_key is None
    assert settings.mock_response_delay_ms == 0


def test_settings_parse_environment_overrides(monkeypatch):
    clear_settings_env(monkeypatch)
    monkeypatch.setenv("APP_NAME", "Matrix Lab")
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("API_V1_PREFIX", "/custom/v1")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://example.com, http://localhost:3000")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-test")
    monkeypatch.setenv("LLM_MOCK_MODE", "false")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("DOUBAO_API_KEY", "test-doubao-key")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setenv("QWEN_API_KEY", "test-qwen-key")
    monkeypatch.setenv("MOCK_RESPONSE_DELAY_MS", "125")

    settings = Settings(_env_file=None)

    assert settings.app_name == "Matrix Lab"
    assert settings.app_version == "1.2.3"
    assert settings.environment == "test"
    assert settings.debug is True
    assert settings.api_v1_prefix == "/custom/v1"
    assert settings.allowed_origins == ["https://example.com", "http://localhost:3000"]
    assert settings.llm_provider == "openai"
    assert settings.llm_model == "gpt-test"
    assert settings.llm_mock_mode is False
    assert settings.openai_api_key == "test-openai-key"
    assert settings.doubao_api_key == "test-doubao-key"
    assert settings.deepseek_api_key == "test-deepseek-key"
    assert settings.qwen_api_key == "test-qwen-key"
    assert settings.mock_response_delay_ms == 125


def test_settings_load_dotenv_file(monkeypatch, tmp_path):
    clear_settings_env(monkeypatch)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "APP_NAME=Dotenv Matrix\n"
        "ALLOWED_ORIGINS=https://dotenv.example,https://admin.example\n"
        "LLM_PROVIDER=deepseek\n"
        "LLM_MODEL=deepseek-test\n"
        "DEEPSEEK_API_KEY=dotenv-key\n",
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.app_name == "Dotenv Matrix"
    assert settings.allowed_origins == ["https://dotenv.example", "https://admin.example"]
    assert settings.llm_provider == "deepseek"
    assert settings.llm_model == "deepseek-test"
    assert settings.deepseek_api_key == "dotenv-key"
    assert settings.llm_mock_mode is True


def test_get_settings_returns_cached_instance(monkeypatch):
    clear_settings_env(monkeypatch)

    first = get_settings()
    second = get_settings()

    assert first is second


def test_env_example_exposes_required_keys():
    env_example = Path(__file__).resolve().parents[2] / ".env.example"

    content = env_example.read_text(encoding="utf-8")

    for key in ENV_KEYS:
        assert f"{key}=" in content
