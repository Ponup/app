from functools import lru_cache

import httpx

from app.core.config import settings


@lru_cache
def _local_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if settings.embedding_provider == "local":
        vectors = _local_model().encode(texts, normalize_embeddings=True)
        result = [vector.tolist() for vector in vectors]
    elif settings.embedding_provider == "openai-compatible":
        if not settings.openai_compatible_base_url:
            raise ValueError("OPENAI_COMPATIBLE_BASE_URL is required")
        response = httpx.post(
            f"{settings.openai_compatible_base_url.rstrip('/')}/embeddings",
            headers={"Authorization": f"Bearer {settings.openai_compatible_api_key}"},
            json={
                "model": settings.openai_compatible_model,
                "input": texts,
                "dimensions": settings.embedding_dimensions,
            },
            timeout=60,
        )
        response.raise_for_status()
        result = [item["embedding"] for item in response.json()["data"]]
    else:
        raise ValueError(f"Unknown embedding provider: {settings.embedding_provider}")
    if any(len(vector) != settings.embedding_dimensions for vector in result):
        raise ValueError(f"Embedding provider must return {settings.embedding_dimensions} dimensions")
    return result
