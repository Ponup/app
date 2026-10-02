import json

import httpx
import pytest

from app.services import image_analysis


def test_disabled_image_analysis_does_not_call_a_model(monkeypatch):
    monkeypatch.setattr(image_analysis.settings, "image_analysis_provider", "disabled")
    assert image_analysis.analyze(b"image", "image/png") is None


def test_ollama_image_analysis_normalizes_and_indexes_response(monkeypatch):
    monkeypatch.setattr(image_analysis.settings, "image_analysis_provider", "ollama")
    monkeypatch.setattr(image_analysis.settings, "image_analysis_model", "llava")
    monkeypatch.setattr(image_analysis.settings, "image_analysis_base_url", "http://ollama:11434")

    def post(url, **kwargs):
        assert url == "http://ollama:11434/api/generate"
        assert kwargs["json"]["images"]
        return httpx.Response(
            200,
            json={"response": json.dumps({
                "description": "A red mug.", "objects": ["mug", "table"], "text": "PONUP"
            })},
            request=httpx.Request("POST", "http://ollama:11434/api/generate"),
        )

    monkeypatch.setattr(image_analysis.httpx, "post", post)
    result = image_analysis.analyze(b"image-bytes", "image/png")
    assert result == {"description": "A red mug.", "objects": ["mug", "table"], "text": "PONUP"}
    assert image_analysis.searchable_text(result) == "A red mug.\n\nVisible objects and features: mug, table\n\nText in image:\nPONUP"


def test_openai_compatible_requires_base_url(monkeypatch):
    monkeypatch.setattr(image_analysis.settings, "image_analysis_provider", "openai-compatible")
    monkeypatch.setattr(image_analysis.settings, "image_analysis_model", "gpt-4.1-mini")
    monkeypatch.setattr(image_analysis.settings, "image_analysis_base_url", "")
    with pytest.raises(ValueError, match="BASE_URL"):
        image_analysis.analyze(b"image", "image/jpeg")
