"""Extract searchable facts from image uploads through a vision-capable model."""

import base64
import json
from typing import Any

import httpx

from app.core.config import settings

_PROMPT = """Analyze this image for a knowledge base. Return JSON only with these keys:
description (a concise factual description), objects (an array of visible objects, people,
places, or notable visual features), and text (all legible text, preserving line breaks).
Do not guess details that are not visible. Use empty strings or arrays when nothing applies."""


def _json_object(value: str) -> dict[str, Any]:
    value = value.strip()
    if value.startswith("```"):
        value = value.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Vision model response must be a JSON object")
    objects = parsed.get("objects", [])
    if not isinstance(objects, list) or not all(isinstance(item, str) for item in objects):
        raise ValueError("Vision model response field 'objects' must be an array of strings")
    description = parsed.get("description", "")
    text = parsed.get("text", "")
    if not isinstance(description, str) or not isinstance(text, str):
        raise ValueError("Vision model response fields 'description' and 'text' must be strings")
    return {"description": description.strip(), "objects": objects, "text": text.strip()}


def analyze(data: bytes, mime_type: str) -> dict[str, Any] | None:
    """Return normalized image facts, or None when image analysis is disabled."""
    provider = settings.image_analysis_provider.lower()
    if provider == "disabled":
        return None
    if not settings.image_analysis_model:
        raise ValueError("IMAGE_ANALYSIS_MODEL is required when image analysis is enabled")
    encoded = base64.b64encode(data).decode("ascii")
    if provider == "ollama":
        base_url = settings.image_analysis_base_url or "http://localhost:11434"
        response = httpx.post(
            f"{base_url.rstrip('/')}/api/generate",
            json={
                "model": settings.image_analysis_model,
                "prompt": _PROMPT,
                "images": [encoded],
                "stream": False,
                "format": "json",
            },
            timeout=settings.image_analysis_timeout_seconds,
        )
        response.raise_for_status()
        return _json_object(response.json()["response"])
    if provider == "openai-compatible":
        if not settings.image_analysis_base_url:
            raise ValueError("IMAGE_ANALYSIS_BASE_URL is required for an OpenAI-compatible model")
        headers = {"Content-Type": "application/json"}
        if settings.image_analysis_api_key:
            headers["Authorization"] = f"Bearer {settings.image_analysis_api_key}"
        response = httpx.post(
            f"{settings.image_analysis_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json={
                "model": settings.image_analysis_model,
                "messages": [{"role": "user", "content": [
                    {"type": "text", "text": _PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded}"}},
                ]}],
                "response_format": {"type": "json_object"},
                "temperature": 0,
            },
            timeout=settings.image_analysis_timeout_seconds,
        )
        response.raise_for_status()
        return _json_object(response.json()["choices"][0]["message"]["content"])
    raise ValueError(f"Unknown image analysis provider: {settings.image_analysis_provider}")


def searchable_text(analysis: dict[str, Any]) -> str:
    """Make the model's image facts available to the existing text embedding pipeline."""
    sections = [analysis.get("description", "")]
    if analysis.get("objects"):
        sections.append("Visible objects and features: " + ", ".join(analysis["objects"]))
    if analysis.get("text"):
        sections.append("Text in image:\n" + analysis["text"])
    return "\n\n".join(value for value in sections if value).strip()
