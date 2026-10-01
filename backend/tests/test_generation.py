import json

import httpx
import pytest
from fastapi import HTTPException

from app.models import ContentKind
from app.services import generation


def test_generation_requires_configuration(monkeypatch):
    monkeypatch.setattr(generation.settings, "llm_base_url", "")
    monkeypatch.setattr(generation.settings, "llm_model", "")
    with pytest.raises(HTTPException, match="not configured"):
        generation.generate_content("Guide", "", [], ContentKind.markdown)


def test_generation_parses_json_response(monkeypatch):
    monkeypatch.setattr(generation.settings, "llm_base_url", "https://llm.example/v1")
    monkeypatch.setattr(generation.settings, "llm_model", "test-model")

    def post(*args, **kwargs):
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"topic": "Guide"})}}]})

    monkeypatch.setattr(generation.httpx, "post", post)
    assert generation.generate_content("Guide", "", [], ContentKind.json) == {"topic": "Guide"}
