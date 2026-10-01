import json

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.models import ContentKind


def _prompt(title: str, description: str, tags: list[str], kind: ContentKind) -> str:
    details = [f"Title: {title}"]
    if description:
        details.append(f"Description: {description}")
    if tags:
        details.append(f"Tags: {', '.join(tags)}")
    requested_format = (
        "Return valid JSON only, with no Markdown fence or commentary."
        if kind == ContentKind.json
        else "Return polished Markdown only, with no preamble or Markdown fence."
    )
    return (
        "Write useful, accurate source content for a knowledge base from the supplied metadata. "
        "Do not invent specific facts that are not implied by that metadata; use broadly useful "
        "structure and clearly label assumptions where needed. "
        f"{requested_format}\n\n" + "\n".join(details)
    )


def generate_content(title: str, description: str, tags: list[str], kind: ContentKind):
    if not settings.llm_base_url or not settings.llm_model:
        raise HTTPException(
            503,
            "Content generation is not configured. Set LLM_BASE_URL and LLM_MODEL on the server.",
        )
    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"
    try:
        response = httpx.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json={
                "model": settings.llm_model,
                "messages": [
                    {"role": "system", "content": "You generate concise, trustworthy knowledge-base content."},
                    {"role": "user", "content": _prompt(title, description, tags, kind)},
                ],
                "temperature": 0.4,
            },
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()["choices"][0]["message"]["content"].strip()
    except (httpx.HTTPError, IndexError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(502, f"Content generation failed: {error}") from error
    if not body:
        raise HTTPException(502, "Content generation returned an empty response")
    if kind == ContentKind.json:
        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise HTTPException(502, "Content generation did not return valid JSON") from error
    return body
