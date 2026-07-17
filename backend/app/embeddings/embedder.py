"""Azure OpenAI embeddings (text-embedding-3-large)."""
from openai import AzureOpenAI, OpenAI

from app.config.settings import get_settings

settings = get_settings()


def _client() -> AzureOpenAI | OpenAI:
    if settings.llm_provider == "ollama":
        return OpenAI(base_url=f"{settings.ollama_base_url.rstrip('/')}/v1", api_key="ollama")
    return AzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    client = _client()
    model = (settings.ollama_embedding_model if settings.llm_provider == "ollama"
             else settings.azure_openai_embedding_deployment)
    out: list[list[float]] = []
    for i in range(0, len(texts), 64):  # batch to stay under token limits
        resp = client.embeddings.create(model=model, input=texts[i:i + 64])
        out.extend(d.embedding for d in resp.data)
    return out
