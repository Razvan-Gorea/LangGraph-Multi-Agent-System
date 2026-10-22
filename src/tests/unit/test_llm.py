from unittest.mock import patch

from application.llm import get_llm

def test_get_llm_uses_configured_provider_and_model(mock_env):
    mock_env.LLM_PROVIDER = "anthropic"
    mock_env.LLM_MODEL = "some-model"

    with patch("application.llm.init_chat_model") as init:
        get_llm(mock_env, 123)

    args, kwargs = init.call_args
    assert args == ("some-model",)
    assert kwargs["model_provider"] == "anthropic"
    assert kwargs["max_tokens"] == 123
    assert kwargs["api_key"] == "test_api_key"
