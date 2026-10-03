import base64
import uuid
from unittest.mock import MagicMock

import pytest

from app.mcp.server import _content, download_content
from app.models import Content, ContentKind


def test_content_lookup_by_uuid_and_slug():
    mock_db = MagicMock()
    content_id = uuid.uuid4()
    mock_content = Content(
        id=content_id,
        slug="test-slug",
        title="Test Title",
        kind=ContentKind.markdown,
        mime_type="text/markdown",
        size=10,
        checksum="abcd",
        object_key="spaces/abc/contents/123/source",
    )

    # Lookup by UUID
    mock_db.get.return_value = mock_content
    result = _content(mock_db, str(content_id))
    assert result == mock_content

    # Lookup by slug
    mock_db.get.return_value = None
    mock_db.scalar.return_value = mock_content
    result = _content(mock_db, "test-slug")
    assert result == mock_content

    # Lookup not found
    mock_db.scalar.return_value = None
    with pytest.raises(ValueError, match="Content not found"):
        _content(mock_db, "nonexistent")


def test_download_content_binary(monkeypatch):
    content_id = uuid.uuid4()
    mock_content = Content(
        id=content_id,
        slug="ponup-logo",
        title="Ponup logo",
        kind=ContentKind.file,
        mime_type="image/png",
        size=4,
        checksum="1234",
        object_key="spaces/abc/contents/123/icon.png",
        custom_metadata={"filename": "icon.png"},
    )

    mock_db = MagicMock()
    mock_db.__enter__.return_value = mock_db
    mock_db.get.return_value = mock_content

    monkeypatch.setattr("app.mcp.server.SessionLocal", lambda: mock_db)
    monkeypatch.setattr("app.mcp.server.storage.get", lambda key: b"\x89PNG")

    result = download_content(str(content_id))
    assert result["id"] == str(content_id)
    assert result["slug"] == "ponup-logo"
    assert result["title"] == "Ponup logo"
    assert result["filename"] == "icon.png"
    assert result["mime_type"] == "image/png"
    assert result["size"] == 4
    assert result["encoding"] == "base64"
    assert result["data"] == base64.b64encode(b"\x89PNG").decode("ascii")
    assert result["text"] is None


def test_download_content_text(monkeypatch):
    content_id = uuid.uuid4()
    mock_content = Content(
        id=content_id,
        slug="sample-doc",
        title="Sample Doc",
        kind=ContentKind.markdown,
        mime_type="text/markdown",
        size=13,
        checksum="5678",
        object_key="spaces/abc/contents/123/source",
        custom_metadata={},
    )

    mock_db = MagicMock()
    mock_db.__enter__.return_value = mock_db
    mock_db.get.return_value = mock_content

    monkeypatch.setattr("app.mcp.server.SessionLocal", lambda: mock_db)
    monkeypatch.setattr("app.mcp.server.storage.get", lambda key: b"# Hello World")

    result = download_content(str(content_id))
    assert result["filename"] == "sample-doc.md"
    assert result["mime_type"] == "text/markdown"
    assert result["text"] == "# Hello World"
    assert result["data"] == base64.b64encode(b"# Hello World").decode("ascii")
