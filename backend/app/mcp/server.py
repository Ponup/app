import base64
import json
import uuid

from mcp.server.fastmcp import FastMCP
from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import Content, Space, Visibility
from app.schemas import ContentCreate, ContentOut, ContentUpdate, SpaceCreate, SpaceOut, SpaceUpdate
from app.services import content as service
from app.services import storage
from app.worker import enqueue

mcp = FastMCP(
    "Ponup",
    instructions="Manage Spaces and Content, and retrieve context with semantic search.",
    streamable_http_path="/mcp",
)


def _space(db, value: str) -> Space:
    try:
        found = db.get(Space, uuid.UUID(value))
    except ValueError:
        found = db.scalar(select(Space).where(Space.slug == value))
    if not found:
        raise ValueError("Space not found")
    return found


def _content(db, value: str) -> Content:
    try:
        found = db.get(Content, uuid.UUID(value))
    except ValueError:
        found = None
    if not found:
        found = db.scalar(select(Content).where(Content.slug == value))
    if not found:
        raise ValueError("Content not found")
    return found


def _dump(value) -> dict:
    return value.model_dump(mode="json", by_alias=True)


@mcp.tool()
def list_spaces() -> list[dict]:
    """List every Space."""
    with SessionLocal() as db:
        return [_dump(SpaceOut.model_validate(value)) for value in db.scalars(select(Space))]


@mcp.tool()
def get_space(space: str) -> dict:
    """Get a Space by UUID or slug."""
    with SessionLocal() as db:
        return _dump(SpaceOut.model_validate(_space(db, space)))


@mcp.tool()
def create_space(name: str, description: str = "", slug: str | None = None) -> dict:
    """Create a Space."""
    with SessionLocal() as db:
        return _dump(SpaceOut.model_validate(service.create_space(db, SpaceCreate(name=name, description=description, slug=slug))))


@mcp.tool()
def update_space(space: str, name: str | None = None, description: str | None = None) -> dict:
    """Update a Space's name or description."""
    with SessionLocal() as db:
        result = service.update_space(db, _space(db, space), SpaceUpdate(name=name, description=description))
        return _dump(SpaceOut.model_validate(result))


@mcp.tool()
def delete_space(space: str) -> str:
    """Permanently delete a Space and all of its Content."""
    with SessionLocal() as db:
        value = _space(db, space)
        for item in list(value.contents):
            service.delete_content(db, item)
        db.delete(value)
        db.commit()
    return "deleted"


@mcp.tool()
def list_contents(space: str, tags: list[str] | None = None) -> list[dict]:
    """List Content in a Space, optionally requiring tags."""
    with SessionLocal() as db:
        value = _space(db, space)
        statement = select(Content).where(Content.space_id == value.id)
        if tags:
            statement = statement.where(Content.tags.contains(tags))
        return [_dump(ContentOut.model_validate(item)) for item in db.scalars(statement)]


@mcp.tool()
def get_content(content_id: str, include_body: bool = True) -> dict:
    """Get Content metadata and, for authored Content, its body."""
    with SessionLocal() as db:
        value = _content(db, content_id)
        result = _dump(ContentOut.model_validate(value))
        if include_body and value.kind.value != "file":
            result["body"] = service.body_for(value)
        return result


@mcp.tool()
def download_content(content_id: str) -> dict:
    """Download the raw file data or body of Content as base64-encoded bytes with metadata."""
    with SessionLocal() as db:
        value = _content(db, content_id)
        raw = storage.get(value.object_key)
        filename = (value.custom_metadata or {}).get("filename")
        if not filename:
            if value.kind.value == "markdown":
                filename = f"{value.slug}.md"
            elif value.kind.value == "json":
                filename = f"{value.slug}.json"
            else:
                filename = value.slug
        text = (
            raw.decode("utf-8", errors="replace")
            if (
                value.mime_type.startswith("text/")
                or value.mime_type == "application/json"
                or value.kind.value in ("markdown", "json")
            )
            else None
        )
        return {
            "id": str(value.id),
            "slug": value.slug,
            "title": value.title,
            "filename": filename,
            "mime_type": value.mime_type,
            "size": value.size,
            "encoding": "base64",
            "data": base64.b64encode(raw).decode("ascii"),
            "text": text,
        }


@mcp.tool()
def create_content(
    space: str,
    title: str,
    body: str,
    kind: str = "markdown",
    description: str = "",
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    """Create authored Markdown or JSON Content and queue it for indexing."""
    with SessionLocal() as db:
        value = service.create_content(
            db,
            _space(db, space),
            ContentCreate(
                title=title,
                body=body,
                kind=kind,
                description=description,
                tags=tags or [],
                metadata=metadata or {},
            ),
        )
        enqueue(value.id)
        return _dump(ContentOut.model_validate(value))


@mcp.tool()
def update_content(
    content_id: str,
    title: str | None = None,
    body: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    """Update Content. Supplying a body queues reindexing."""
    with SessionLocal() as db:
        data = ContentUpdate(
            **{
                key: value
                for key, value in {
                    "title": title,
                    "body": body,
                    "description": description,
                    "tags": tags,
                    "metadata": metadata,
                }.items()
                if value is not None
            }
        )
        value, changed = service.update_content(db, _content(db, content_id), data)
        if changed:
            enqueue(value.id)
        return _dump(ContentOut.model_validate(value))


@mcp.tool()
def publish_content(content_id: str, published: bool = True) -> dict:
    """Publish or unpublish Content."""
    with SessionLocal() as db:
        value = service.set_visibility(
            db, _content(db, content_id), Visibility.public if published else Visibility.private
        )
        return _dump(ContentOut.model_validate(value))


@mcp.tool()
def delete_content(content_id: str) -> str:
    """Permanently delete Content."""
    with SessionLocal() as db:
        service.delete_content(db, _content(db, content_id))
    return "deleted"


@mcp.tool()
def search_content(space: str, query: str, top_k: int = 10, tags: list[str] | None = None) -> list[dict]:
    """Return semantically ranked passages from a Space."""
    with SessionLocal() as db:
        value = _space(db, space)
        return [item.model_dump(mode="json") for item in service.search(db, value.id, query, top_k, tags)]


@mcp.resource("ponup://spaces/{space_slug}/contents/{content_slug}")
def content_resource(space_slug: str, content_slug: str) -> str:
    """Read a Content body via its stable Space and Content slugs."""
    with SessionLocal() as db:
        value = db.scalar(
            select(Content).join(Space).where(Space.slug == space_slug, Content.slug == content_slug)
        )
        if not value:
            raise ValueError("Content not found")
        if value.kind.value == "file":
            return json.dumps(_dump(ContentOut.model_validate(value)))
        body = service.body_for(value)
        return body if isinstance(body, str) else json.dumps(body, ensure_ascii=False, indent=2)
