import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models import Content, ProcessingStatus, Space, Visibility
from app.schemas import (
    ContentCreate,
    ContentDetail,
    ContentGenerate,
    ContentGenerateOut,
    ContentOut,
    ContentUpdate,
    SearchResponse,
    SpaceCreate,
    SpaceOut,
    SpaceUpdate,
)
from app.services import content as service
from app.services import generation
from app.services import storage
from app.worker import enqueue

router = APIRouter(prefix="/api/v1")
public_router = APIRouter(prefix="/public/v1")


def space_or_404(db: Session, space_id: uuid.UUID) -> Space:
    if space := db.get(Space, space_id):
        return space
    raise HTTPException(404, "Space not found")


def content_or_404(db: Session, content_id: uuid.UUID) -> Content:
    if content := db.get(Content, content_id):
        return content
    raise HTTPException(404, "Content not found")


@router.get("/spaces", response_model=list[SpaceOut])
def list_spaces(db: Session = Depends(get_db)):
    return db.scalars(select(Space).order_by(Space.name)).all()


@router.post("/spaces", response_model=SpaceOut, status_code=201)
def create_space(data: SpaceCreate, db: Session = Depends(get_db)):
    return service.create_space(db, data)


@router.get("/spaces/{space_id}", response_model=SpaceOut)
def get_space(space_id: uuid.UUID, db: Session = Depends(get_db)):
    return space_or_404(db, space_id)


@router.patch("/spaces/{space_id}", response_model=SpaceOut)
def update_space(space_id: uuid.UUID, data: SpaceUpdate, db: Session = Depends(get_db)):
    return service.update_space(db, space_or_404(db, space_id), data)


@router.delete("/spaces/{space_id}", status_code=204)
def delete_space(space_id: uuid.UUID, db: Session = Depends(get_db)):
    space = space_or_404(db, space_id)
    keys = list(db.scalars(select(Content.object_key).where(Content.space_id == space.id)))
    db.delete(space)
    db.commit()
    for key in keys:
        storage.delete(key)


@router.get("/spaces/{space_id}/contents", response_model=list[ContentOut])
def list_contents(
    space_id: uuid.UUID,
    tag: list[str] = Query(default=[]),
    db: Session = Depends(get_db),
):
    space_or_404(db, space_id)
    statement = select(Content).where(Content.space_id == space_id).order_by(Content.updated_at.desc())
    if tag:
        statement = statement.where(Content.tags.contains(tag))
    return db.scalars(statement).all()


@router.post("/spaces/{space_id}/contents", response_model=ContentOut, status_code=201)
def create_content(space_id: uuid.UUID, data: ContentCreate, db: Session = Depends(get_db)):
    content = service.create_content(db, space_or_404(db, space_id), data)
    enqueue(content.id)
    return content


@router.post("/spaces/{space_id}/contents/generate", response_model=ContentGenerateOut)
def generate_content(space_id: uuid.UUID, data: ContentGenerate, db: Session = Depends(get_db)):
    space_or_404(db, space_id)
    return {"body": generation.generate_content(data.title, data.description, data.tags, data.kind)}


@router.post("/spaces/{space_id}/uploads", response_model=ContentOut, status_code=201)
async def upload_content(
    space_id: uuid.UUID,
    file: UploadFile = File(),
    title: str | None = Form(default=None),
    description: str = Form(default=""),
    tags: str = Form(default=""),
    db: Session = Depends(get_db),
):
    raw = await file.read(settings.max_upload_bytes + 1)
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(413, "Upload exceeds configured size limit")
    if not raw:
        raise HTTPException(422, "Uploaded file is empty")
    content = service.create_upload(
        db,
        space_or_404(db, space_id),
        title=title or file.filename or "Untitled upload",
        filename=file.filename or "upload",
        mime_type=file.content_type or "application/octet-stream",
        raw=raw,
        description=description,
        tags=[value.strip().lower() for value in tags.split(",") if value.strip()],
    )
    enqueue(content.id)
    return content


@router.get("/contents/{content_id}", response_model=ContentDetail)
def get_content(content_id: uuid.UUID, db: Session = Depends(get_db)):
    content = content_or_404(db, content_id)
    result = ContentOut.model_validate(content).model_dump()
    result["body"] = service.body_for(content) if content.kind.value != "file" else None
    return result


@router.get("/contents/{content_id}/raw")
def get_raw(content_id: uuid.UUID, db: Session = Depends(get_db)):
    content = content_or_404(db, content_id)
    return Response(storage.get(content.object_key), media_type=content.mime_type)


@router.patch("/contents/{content_id}", response_model=ContentOut)
def update_content(content_id: uuid.UUID, data: ContentUpdate, db: Session = Depends(get_db)):
    content, body_changed = service.update_content(db, content_or_404(db, content_id), data)
    if body_changed:
        enqueue(content.id)
    return content


@router.delete("/contents/{content_id}", status_code=204)
def delete_content(content_id: uuid.UUID, db: Session = Depends(get_db)):
    service.delete_content(db, content_or_404(db, content_id))


@router.post("/contents/{content_id}/publish", response_model=ContentOut)
def publish_content(content_id: uuid.UUID, db: Session = Depends(get_db)):
    return service.set_visibility(db, content_or_404(db, content_id), Visibility.public)


@router.post("/contents/{content_id}/unpublish", response_model=ContentOut)
def unpublish_content(content_id: uuid.UUID, db: Session = Depends(get_db)):
    return service.set_visibility(db, content_or_404(db, content_id), Visibility.private)


@router.post("/contents/{content_id}/retry", response_model=ContentOut)
def retry_content(content_id: uuid.UUID, db: Session = Depends(get_db)):
    content = content_or_404(db, content_id)
    content.processing_status = ProcessingStatus.queued
    content.processing_error = None
    db.commit()
    enqueue(content.id)
    return content


@router.get("/spaces/{space_id}/search", response_model=SearchResponse)
def search_content(
    space_id: uuid.UUID,
    q: str = Query(min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
    tag: list[str] = Query(default=[]),
    db: Session = Depends(get_db),
):
    space_or_404(db, space_id)
    return SearchResponse(query=q, results=service.search(db, space_id, q, top_k, tag))


def public_content(db: Session, space_slug: str, content_slug: str) -> Content:
    content = db.scalar(
        select(Content)
        .join(Space)
        .where(
            Space.slug == space_slug,
            Content.slug == content_slug,
            Content.visibility == Visibility.public,
        )
    )
    if not content:
        raise HTTPException(404, "Published content not found")
    return content


@public_router.get("/spaces/{space_slug}/contents/{content_slug}")
def public_metadata(space_slug: str, content_slug: str, db: Session = Depends(get_db)):
    content = public_content(db, space_slug, content_slug)
    return ContentOut.model_validate(content)


@public_router.get("/spaces/{space_slug}/contents/{content_slug}/raw")
def public_raw(space_slug: str, content_slug: str, db: Session = Depends(get_db)):
    content = public_content(db, space_slug, content_slug)
    return Response(storage.get(content.object_key), media_type=content.mime_type)


@public_router.get("/spaces/{space_slug}/contents/{content_slug}/body")
def public_body(space_slug: str, content_slug: str, db: Session = Depends(get_db)):
    content = public_content(db, space_slug, content_slug)
    if content.mime_type == "application/json":
        return service.body_for(content)
    return {"body": service.body_for(content) if content.kind.value != "file" else None}
