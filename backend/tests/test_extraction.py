import json

import pytest

from app.services.extraction import chunk, extract


def test_extracts_and_formats_json():
    result = extract(b'{"answer":42}', "application/json")
    assert json.loads(result) == {"answer": 42}


def test_rejects_malformed_json():
    with pytest.raises(json.JSONDecodeError):
        extract(b"not json", "application/json")


def test_non_indexed_type_returns_none():
    assert extract(b"image", "image/png") is None


def test_chunks_with_overlap_without_empty_values():
    result = chunk("paragraph one\n\n" + "x" * 100, size=40, overlap=10)
    assert len(result) > 2
    assert all(result)
