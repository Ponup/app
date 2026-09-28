import pytest
from pydantic import ValidationError

from app.models import ContentKind
from app.schemas import ContentCreate, SpaceCreate


def test_space_requires_a_name():
    with pytest.raises(ValidationError):
        SpaceCreate(name="")


def test_content_normalizes_tags():
    value = ContentCreate(title="Guide", kind=ContentKind.markdown, body="# Guide", tags=[" Guide ", "guide", "AI"])
    assert value.tags == ["ai", "guide"]


def test_json_accepts_structured_body():
    value = ContentCreate(title="Data", kind=ContentKind.json, body={"ok": True})
    assert value.body == {"ok": True}
