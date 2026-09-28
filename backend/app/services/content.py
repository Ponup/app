import hashlib
import json
import re
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Content, ContentChunk, ContentKind, ProcessingStatus, Space, Visibility
from app.schemas import ContentCreate, ContentUpdate, SearchResult, SpaceCreate, SpaceUpdate
from app.services import embeddings, storage


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:100] or "untitled"


def unique_space_slug(db: Session, desired: str, exclude: uuid.UUID | None = None) -> str:
    base = slugify(desired)
    candidate = base
    index = 2
    while db.scalar(select(Space.id).where(Space.slug == candidate, Space.id != exclude)):
        candidate = f"{base[:95]}-{index}"
        index += 1
    return candidate


def unique_content_slug(
    db: Session, space_id: uuid.UUID, desired: str, exclude: uuid.UUID | None = None
) -> str:
    base = slugify(desired)
    candidate = base
    index = 2
    while db.scalar(
        select(Content.id).where(
            Content.space_id == space_id, Content.slug == candidate, Content.id != exclude
        )
    ):
        candidate = f"{base[:95]}-{index}"
        index += 1
    return candidate


def create_space(db: Session, data: SpaceCreate) -> Space:
    space = Space(
        name=data.name,
        slug=unique_space_slug(db, data.slug or data.name),
        description=data.description,
    )
    db.add(space)
    db.commit()
    db.refresh(space)
    return space


def update_space(db: Session, space: Space, data: SpaceUpdate) -> Space:
    values = data.model_dump(exclude_unset=True)
    if "slug" in values:
        values["slug"] = unique_space_slug(db, values["slug"], space.id)
    for key, value in values.items():
        setattr(space, key, value)
    db.commit()
    db.refresh(space)
    return space


def serialize_body(body: str | dict[str, Any] | list[Any], kind: ContentKind) -> tuple[bytes, str]:
    if kind == ContentKind.json:
        value = body if not isinstance(body, str) else json.loads(body)
        return json.dumps(value, ensure_ascii=False, indent=2).encode(), "application/json"
    if not isinstance(body, str):
        raise ValueError("Markdown content body must be a string")
    return body.encode(), "text/markdown"


def create_content(db: Session, space: Space, data: ContentCreate) -> Content:
    raw, mime_type = serialize_body(data.body, data.kind)
    content_id = uuid.uuid4()
    object_key = f"spaces/{space.id}/contents/{content_id}/source"
    storage.put(object_key, raw, mime_type)
    content = Content(
        id=content_id,
        space_id=space.id,
        slug=unique_content_slug(db, space.id, data.slug or data.title),
        title=data.title,
        description=data.description,
        kind=data.kind,
        mime_type=mime_type,
        tags=data.tags,
        custom_metadata=data.metadata,
        object_key=object_key,
        checksum=hashlib.sha256(raw).hexdigest(),
        size=len(raw),
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def create_upload(
    db: Session,
    space: Space,
    *,
    title: str,
    filename: str,
    mime_type: str,
    raw: bytes,
    description: str = "",
    tags: list[str] | None = None,
) -> Content:
    content_id = uuid.uuid4()
    object_key = f"spaces/{space.id}/contents/{content_id}/{slugify(filename)}"
    storage.put(object_key, raw, mime_type)
    content = Content(
        id=content_id,
        space_id=space.id,
        slug=unique_content_slug(db, space.id, title),
        title=title,
        description=description,
        kind=ContentKind.file,
        mime_type=mime_type,
        tags=sorted(set(tags or [])),
        custom_metadata={"filename": filename},
        object_key=object_key,
        checksum=hashlib.sha256(raw).hexdigest(),
        size=len(raw),
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def update_content(db: Session, content: Content, data: ContentUpdate) -> tuple[Content, bool]:
    values = data.model_dump(exclude_unset=True)
    body_changed = "body" in values
    if "slug" in values:
        values["slug"] = unique_content_slug(db, content.space_id, values["slug"], content.id)
    if "metadata" in values:
        values["custom_metadata"] = values.pop("metadata")
    body = values.pop("body", None)
    if body_changed:
        raw, _ = serialize_body(body, content.kind)
        storage.put(content.object_key, raw, content.mime_type)
        content.checksum = hashlib.sha256(raw).hexdigest()
        content.size = len(raw)
        content.processing_status = ProcessingStatus.queued
        content.processing_error = None
    if "tags" in values:
        values["tags"] = sorted({tag.strip().lower() for tag in values["tags"] if tag.strip()})
    for key, value in values.items():
        setattr(content, key, value)
    db.commit()
    db.refresh(content)
    return content, body_changed


def delete_content(db: Session, content: Content) -> None:
    object_key = content.object_key
    db.delete(content)
    db.commit()
    storage.delete(object_key)


def body_for(content: Content) -> str | dict[str, Any] | list[Any]:
    raw = storage.get(content.object_key)
    if content.mime_type == "application/json":
        return json.loads(raw)
    return raw.decode("utf-8")


def set_visibility(db: Session, content: Content, visibility: Visibility) -> Content:
    content.visibility = visibility
    db.commit()
    db.refresh(content)
    return content


def search(
    db: Session, space_id: uuid.UUID, query: str, top_k: int = 10, tags: list[str] | None = None
) -> list[SearchResult]:
    vector = embeddings.embed([query])[0]
    distance = ContentChunk.embedding.cosine_distance(vector)
    statement = (
        select(ContentChunk, Content, distance.label("distance"))
        .join(Content)
        .where(
            Content.space_id == space_id,
            Content.processing_status == ProcessingStatus.ready,
        )
        .order_by(distance)
        .limit(max(1, min(top_k, 50)))
    )
    if tags:
        statement = statement.where(Content.tags.contains(tags))
    return [
        SearchResult(
            content_id=content.id,
            content_slug=content.slug,
            title=content.title,
            description=content.description,
            tags=content.tags,
            chunk_position=chunk.position,
            text=chunk.text,
            score=max(0.0, 1.0 - float(distance_value)),
        )
        for chunk, content, distance_value in db.execute(statement)
    ]
