from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from application.agents.extras import GraphCallback
from application.environment import Environment

def get_llm(env: Environment, max_tokens: int) -> BaseChatModel:
    """Chat model chosen by LLM_PROVIDER / LLM_MODEL. Non-default providers need their langchain-<provider> package."""
    return init_chat_model(
        env.LLM_MODEL,
        model_provider=env.LLM_PROVIDER,
        max_retries=2,
        max_tokens=max_tokens,
        api_key=env.LLM_API_KEY,
        callbacks=[GraphCallback()],
    )
