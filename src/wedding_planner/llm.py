"""Chat model factory. Provider and model come from settings, so they can be swapped via .env."""

from langchain.chat_models import init_chat_model

from .config import get_settings


def get_model():
    s = get_settings()
    return init_chat_model(
        model=s.llm_model,
        model_provider=s.llm_provider,
        max_retries=s.llm_max_retries,
    )
