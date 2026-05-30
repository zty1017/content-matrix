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
    "ASR_PROVIDER",
    "ASR_MOCK_MODE",
    "ASR_DOUBAO_RESOURCE_ID",
    "ASR_REQUEST_TIMEOUT_SECONDS",
    "ASR_MAX_AUDIO_SIZE_MB",
    "DEEPSEEK_API_KEY",
    "QWEN_API_KEY",
    "MEITUAN_API_KEY",
    "MEITUAN_BASE_URL",
    "LLM_REQUEST_TIMEOUT_SECONDS",
    "LLM_MAX_TOKENS",
    "LLM_TEMPERATURE",
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
    assert settings.asr_provider == "mock"
    assert settings.asr_mock_mode is True
    assert settings.asr_doubao_resource_id == "volc.bigasr.auc_turbo"
    assert settings.asr_request_timeout_seconds == 30.0
    assert settings.asr_max_audio_size_mb == 50
    assert settings.deepseek_api_key is None
    assert settings.qwen_api_key is None
    assert settings.meituan_api_key is None
    assert settings.meituan_base_url == "https://api.longcat.chat/openai"
    assert settings.llm_request_timeout_seconds == 30.0
    assert settings.llm_max_tokens == 1024
    assert settings.llm_temperature == 0.7
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
    monkeypatch.setenv("ASR_PROVIDER", "doubao_flash")
    monkeypatch.setenv("ASR_MOCK_MODE", "false")
    monkeypatch.setenv("ASR_DOUBAO_RESOURCE_ID", "volc.bigasr.auc_turbo")
    monkeypatch.setenv("ASR_REQUEST_TIMEOUT_SECONDS", "9.5")
    monkeypatch.setenv("ASR_MAX_AUDIO_SIZE_MB", "80")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setenv("QWEN_API_KEY", "test-qwen-key")
    monkeypatch.setenv("MEITUAN_API_KEY", "test-meituan-key")
    monkeypatch.setenv("MEITUAN_BASE_URL", "https://example.longcat/openai")
    monkeypatch.setenv("LLM_REQUEST_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("LLM_MAX_TOKENS", "2048")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.3")
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
    assert settings.asr_provider == "doubao_flash"
    assert settings.asr_mock_mode is False
    assert settings.asr_doubao_resource_id == "volc.bigasr.auc_turbo"
    assert settings.asr_request_timeout_seconds == 9.5
    assert settings.asr_max_audio_size_mb == 80
    assert settings.deepseek_api_key == "test-deepseek-key"
    assert settings.qwen_api_key == "test-qwen-key"
    assert settings.meituan_api_key == "test-meituan-key"
    assert settings.meituan_base_url == "https://example.longcat/openai"
    assert settings.llm_request_timeout_seconds == 12.5
    assert settings.llm_max_tokens == 2048
    assert settings.llm_temperature == 0.3
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
