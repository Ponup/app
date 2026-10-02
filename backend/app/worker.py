import uuid

from celery import Celery
from sqlalchemy import delete

from app.core.config import settings
from app.core.db import SessionLocal
from app.models import Content, ContentChunk, ProcessingStatus
from app.services import embeddings, extraction, image_analysis, storage

celery = Celery("ponup", broker=settings.redis_url, backend=settings.redis_url)
celery.conf.update(task_track_started=True, task_acks_late=True, worker_prefetch_multiplier=1)


@celery.task(autoretry_for=(ConnectionError,), retry_backoff=True, max_retries=5)
def process_content(content_id: str) -> None:
    with SessionLocal() as db:
        content = db.get(Content, uuid.UUID(content_id))
        if not content:
            return
        content.processing_status = ProcessingStatus.processing
        content.processing_error = None
        db.commit()
        try:
            raw = storage.get(content.object_key)
            if extraction.is_image(content.mime_type):
                analysis = image_analysis.analyze(raw, content.mime_type)
                content.image_analysis = analysis
                content.extracted_text = analysis["text"] if analysis else None
                text = image_analysis.searchable_text(analysis) if analysis else None
            else:
                content.image_analysis = None
                content.extracted_text = None
                text = extraction.extract(raw, content.mime_type)
            texts = extraction.chunk(text) if text is not None else []
            vectors = embeddings.embed(texts)
            db.execute(delete(ContentChunk).where(ContentChunk.content_id == content.id))
            db.add_all(
                ContentChunk(content_id=content.id, position=index, text=value, embedding=vector)
                for index, (value, vector) in enumerate(zip(texts, vectors, strict=True))
            )
            content.processing_status = ProcessingStatus.ready
            db.commit()
        except Exception as exc:
            db.rollback()
            content = db.get(Content, uuid.UUID(content_id))
            if content:
                content.processing_status = ProcessingStatus.failed
                content.processing_error = str(exc)[:1000]
                db.commit()
            raise


def enqueue(content_id: uuid.UUID) -> None:
    process_content.delay(str(content_id))
