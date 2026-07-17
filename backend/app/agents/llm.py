"""Shared Azure OpenAI chat wrapper (LangChain) with strict-JSON helper."""
import json
import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_llm(temperature: float = 0.1) -> BaseChatModel:
    if settings.llm_provider == "ollama":
        return ChatOpenAI(
            base_url=f"{settings.ollama_base_url.rstrip('/')}/v1",
            api_key="ollama",
            model=settings.ollama_chat_model,
            temperature=temperature,
        )
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_deployment=settings.azure_openai_chat_deployment,
        temperature=temperature,
    )


def run_json(system: str, user: str, temperature: float = 0.1) -> dict:
    llm = get_llm(temperature)
    resp = llm.invoke([("system", system), ("user", user)])
    text = resp.content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[4:] if text.startswith("json") else text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Agent returned non-JSON output; wrapping as raw text")
        return {"raw": resp.content}
