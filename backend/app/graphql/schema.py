import uuid
from datetime import datetime

import strawberry
from sqlalchemy import select
from strawberry.scalars import JSON

from app.core.db import SessionLocal
from app.models import Content, Space
from app.services.content import search


@strawberry.type
class SpaceType:
    id: uuid.UUID
    slug: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@strawberry.type
class ContentType:
    id: uuid.UUID
    space_id: uuid.UUID
    slug: str
    title: str
    description: str
    kind: str
    mime_type: str
    tags: list[str]
    metadata: JSON
    visibility: str
    processing_status: str
    processing_error: str | None
    size: int
    created_at: datetime
    updated_at: datetime


@strawberry.type
class SearchResultType:
    content_id: uuid.UUID
    content_slug: str
    title: str
    description: str
    tags: list[str]
    chunk_position: int
    text: str
    score: float


def map_space(value: Space) -> SpaceType:
    return SpaceType(**{field: getattr(value, field) for field in SpaceType.__annotations__})


def map_content(value: Content) -> ContentType:
    return ContentType(
        id=value.id,
        space_id=value.space_id,
        slug=value.slug,
        title=value.title,
        description=value.description,
        kind=value.kind.value,
        mime_type=value.mime_type,
        tags=value.tags,
        metadata=value.custom_metadata,
        visibility=value.visibility.value,
        processing_status=value.processing_status.value,
        processing_error=value.processing_error,
        size=value.size,
        created_at=value.created_at,
        updated_at=value.updated_at,
    )


@strawberry.type
class Query:
    @strawberry.field
    def spaces(self) -> list[SpaceType]:
        with SessionLocal() as db:
            return [map_space(value) for value in db.scalars(select(Space).order_by(Space.name))]

    @strawberry.field
    def space(self, id: uuid.UUID) -> SpaceType | None:
        with SessionLocal() as db:
            value = db.get(Space, id)
            return map_space(value) if value else None

    @strawberry.field
    def contents(self, space_id: uuid.UUID, tags: list[str] | None = None) -> list[ContentType]:
        with SessionLocal() as db:
            statement = select(Content).where(Content.space_id == space_id)
            if tags:
                statement = statement.where(Content.tags.contains(tags))
            return [map_content(value) for value in db.scalars(statement)]

    @strawberry.field
    def content(self, id: uuid.UUID) -> ContentType | None:
        with SessionLocal() as db:
            value = db.get(Content, id)
            return map_content(value) if value else None

    @strawberry.field
    def semantic_search(
        self, space_id: uuid.UUID, query: str, top_k: int = 10, tags: list[str] | None = None
    ) -> list[SearchResultType]:
        with SessionLocal() as db:
            return [SearchResultType(**value.model_dump()) for value in search(db, space_id, query, top_k, tags)]


schema = strawberry.Schema(query=Query)
