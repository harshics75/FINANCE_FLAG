from fastapi import APIRouter, Depends

from app.auth.dependencies import require_any
from app.config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/info", dependencies=[Depends(require_any)])
def system_info():
    """The actual LLM provider/model currently active — no fake multi-model selector,
    just what's really configured via LLM_PROVIDER."""
    if settings.llm_provider == "ollama":
        return {
            "provider": "ollama",
            "label": "Ollama (local)",
            "chat_model": settings.ollama_chat_model,
            "embedding_model": settings.ollama_embedding_model,
        }
    if settings.llm_provider == "groq":
        return {
            "provider": "groq",
            "label": "Groq",
            "chat_model": settings.groq_chat_model,
            "embedding_model": settings.local_embedding_model,
        }
    return {
        "provider": "azure",
        "label": "Azure OpenAI",
        "chat_model": settings.azure_openai_chat_deployment,
        "embedding_model": settings.azure_openai_embedding_deployment,
    }
