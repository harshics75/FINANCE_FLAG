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
    if settings.llm_provider == "groq":
        return ChatOpenAI(
            base_url=settings.groq_base_url,
            api_key=settings.groq_api_key,
            model=settings.groq_chat_model,
            temperature=temperature,
        )
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_deployment=settings.azure_openai_chat_deployment,
        temperature=temperature,
    )


def _extract_json_object(text: str) -> str | None:
    """Pull the first balanced {...} block out of text that may contain
    stray prose or markdown fences around the JSON the model was asked for."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def run_json(system: str, user: str, temperature: float = 0.1) -> dict:
    llm = get_llm(temperature)
    resp = None
    for attempt in range(2):
        resp = llm.invoke([("system", system), ("user", user)])
        text = resp.content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text[4:] if text.lower().startswith("json") else text
        for candidate in (text, _extract_json_object(text)):
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        logger.warning("Agent returned non-JSON output (attempt %d)", attempt + 1)
        user = user + "\n\nIMPORTANT: Respond with ONLY a single valid JSON object — no prose, no markdown fences."
    return {"raw": resp.content}
