import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ContentKind, ProcessingStatus, Visibility


class SpaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    slug: str | None = Field(default=None, max_length=100)
    description: str = ""


class SpaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    slug: str | None = Field(default=None, max_length=100)
    description: str | None = None


class SpaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    slug: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


class ContentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=100)
    description: str = ""
    kind: ContentKind
    body: str | dict[str, Any] | list[Any]
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        return sorted({tag.strip().lower() for tag in tags if tag.strip()})


class ContentGenerate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2_000)
    kind: ContentKind
    tags: list[str] = Field(default_factory=list)

    @field_validator("kind")
    @classmethod
    def requires_authored_content(cls, kind: ContentKind) -> ContentKind:
        if kind == ContentKind.file:
            raise ValueError("Content generation is only available for Markdown or JSON")
        return kind

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        return sorted({tag.strip().lower() for tag in tags if tag.strip()})


class ContentGenerateOut(BaseModel):
    body: str | dict[str, Any] | list[Any]


class ContentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=100)
    description: str | None = None
    body: str | dict[str, Any] | list[Any] | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class ContentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    space_id: uuid.UUID
    slug: str
    title: str
    description: str
    kind: ContentKind
    mime_type: str
    tags: list[str]
    custom_metadata: dict[str, Any] = Field(serialization_alias="metadata")
    visibility: Visibility
    processing_status: ProcessingStatus
    processing_error: str | None
    image_analysis: dict[str, Any] | None
    extracted_text: str | None
    checksum: str
    size: int
    created_at: datetime
    updated_at: datetime


class ContentDetail(ContentOut):
    body: str | dict[str, Any] | list[Any] | None = None


class SearchResult(BaseModel):
    content_id: uuid.UUID
    content_slug: str
    title: str
    description: str
    tags: list[str]
    chunk_position: int
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
